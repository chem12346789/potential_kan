#!/usr/bin/python3

from absl import flags, app
import torch
from torch import device, save, load, no_grad, any, isnan, autograd, sinh, log
import matplotlib.pyplot as plt
from create_dataset import RhoDataset
from models import KAN

FLAGS = flags.FLAGS

def add_options():
  flags.DEFINE_string('valset', default = None, help = 'file for valset')
  flags.DEFINE_integer('batch_size', default = 4096, help = 'batch size')
  flags.DEFINE_enum('device', default = 'cuda', enum_values = {'cpu', 'cuda'}, help = 'device to use')
  flags.DEFINE_integer('workers', default = 256, help = 'number of workers')

def main(unused_argv):
  evalset = RhoDataset(FLAGS.valset)
  eval_dataloader = DataLoader(evalset, batch_size = FLAGS.batch_size, shuffle = False, num_workers = FLAGS.workers)
  model = KAN(channels = [81*3, 8, 4, 1], grid = 7, k = 3)
  model.to(device(FLAGS.device))
  model.eval()
  exc_trues = list()
  diffs = list()
  for x, e in eval_dataloader:
    x, e = x.to(device(FLAGS.device)), e.to(device(FLAGS.device))
    preds, _ = model(x, do_train = False)
    e_pred = torch.sinh(preds) # e_pred.shape = (batch, 1)
    e_true = torch.sinh(e) # e_true.shape = (batch, 1)
    e_diff = torch.abs(e_pred - e_true)
    exc_trues.append(e_true.detach().cpu().numpy())
    diffs.append(e_diff.detach().cpu().numpy())
  exc_trues = np.squeeze(np.concatenate(exc_trues, axis = 0), axis = -1)
  diffs = np.squeeze(np.concatenate(diffs, axis = 0), axis = -1)
  np.savez('eval.npz', true = exc_trues, diff = diffs)
  plt.set_xlabel('exc ground truth')
  plt.set_ylabel('exc prediction absolute loss')
  plt.scatter(exc_trues, diffs, c = 'b', s = 2, alpha = 0.7)
  plt.savefig('loss_plot.png')

if __name__ == "__main__":
  add_options()
  app.run(main)

