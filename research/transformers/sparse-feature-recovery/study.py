"""Seeded dictionary recovery with reconstruction, support and correlation controls."""
import json
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from recovery import SAE, evaluate


def support_f1(truth, estimate):
    tp = (truth & estimate).sum().item()
    fp = (~truth & estimate).sum().item()
    fn = (truth & ~estimate).sum().item()
    return 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 1.0


def run(seed, data_seed, profile, output):
    torch.set_num_threads(2)
    output = Path(output)
    metrics, conditions = {}, []
    count, steps = (256, 5) if profile == 'smoke' else (10000, 1500)
    train_end, dev_end = int(count*.7), int(count*.85)
    for features in ([30] if profile == 'smoke' else [50, 100, 200]):
        for correlation, noise in [(0., 0.), (.9, 0.), (0., .05)]:
            generator = torch.Generator().manual_seed(data_seed + seed)
            dictionary = torch.randn(30, features, generator=generator)
            dictionary /= dictionary.norm(dim=0)
            if correlation:
                for index in range(1, features, 2):
                    direction = dictionary[:, index] - (dictionary[:, index] @ dictionary[:, index-1])*dictionary[:, index-1]
                    direction /= direction.norm()
                    dictionary[:, index] = correlation*dictionary[:, index-1] + (1-correlation**2)**.5*direction
            truth = (torch.rand(count, features, generator=generator)<.05)*(torch.rand(count, features, generator=generator)+.5)
            observations = truth @ dictionary.T + noise*torch.randn(count, 30, generator=generator)
            torch.manual_seed(seed)
            model = SAE(30, features)
            optimizer = torch.optim.Adam(model.parameters(), lr=.001)
            order_generator = torch.Generator().manual_seed(seed + 100000)
            trace = []
            for step in range(steps):
                indices = torch.randint(train_end, (128,), generator=order_generator)
                optimizer.zero_grad()
                prediction, codes = model(observations[indices])
                loss = F.mse_loss(prediction, observations[indices]) + .01*codes.mean()
                loss.backward()
                optimizer.step()
                model.normalize()
                if step % 100 == 0 or step == steps-1:
                    trace.append(dict(step=step+1, training_loss=float(loss.detach())))
            with torch.no_grad():
                dev_prediction, dev_codes = model(observations[train_end:dev_end])
                final_prediction, final_codes = model(observations[dev_end:])
            matching = evaluate(dictionary.numpy(), model.decoder.weight.detach().numpy())
            # Synthetic ground-truth matching is the declared evaluation instrument.
            true_order = matching['matched_true']
            learned_order = matching['matched_learned']
            dev_truth = truth[train_end:dev_end, true_order] > 0
            candidates = [0., .01, .05, .1, .2, .5]
            threshold = max(candidates, key=lambda t:(support_f1(dev_truth, dev_codes[:,learned_order]>t),t))
            final_truth = truth[dev_end:, true_order] > 0
            prefix = f'features{features}_correlation{correlation}_noise{noise}'
            values = dict(mse=float(F.mse_loss(final_prediction, observations[dev_end:])),
                          zero_reconstruction_mse=float(observations[dev_end:].square().mean()),
                          support_f1=support_f1(final_truth, final_codes[:,learned_order]>threshold),
                          all_positive_support_f1=support_f1(final_truth, torch.ones_like(final_truth)),
                          mean_signed_cosine=float(np.mean(matching['signed_cosines'])),
                          dead_features=float((final_codes.max(0).values == 0).sum()))
            metrics.update({prefix+'.'+k:v for k,v in values.items()})
            np.savez_compressed(output/(prefix+'.npz'), dictionary=dictionary.numpy(),
                                learned=model.decoder.weight.detach().numpy(),
                                truth=truth[dev_end:].numpy(), codes=final_codes.numpy(),
                                observations=observations[dev_end:].numpy(), predictions=final_prediction.numpy())
            torch.save(model.state_dict(), output/(prefix+'.pt'))
            clone = SAE(30, features)
            clone.load_state_dict(torch.load(output/(prefix+'.pt'), weights_only=True))
            with torch.no_grad():
                if not torch.equal(clone(observations[dev_end:])[0], final_prediction):
                    raise ValueError('checkpoint reload changed predictions')
            conditions.append(dict(features=features, correlation=correlation, noise=noise, threshold=threshold,
                                   steps=steps, trace=trace, matching=matching, metrics=values))
    (output/'comparisons.json').write_text(json.dumps(conditions,indent=2,allow_nan=False)+'\n')
    return dict(scope='Synthetic nonnegative sparse codes; independent dictionary/initialisation replicates; threshold selected on development rows; no recovery claim for real-model features.',
                metrics=metrics, split_rows=[train_end,dev_end-train_end,count-dev_end], seed=seed, data_seed=data_seed,
                budget=dict(steps=steps,batch_size=128), checkpoint_rule='fixed final step; no final-set tuning')
