r'''Run BIBD experiments of ResNet based models.'''


import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.backends.cudnn as cudnn
import torchvision
import torchvision.transforms as transforms

import os
import argparse

from utils import progress_bar
from utils import format_time
from models.resnet import ResNet18, ResNet34, ResNet50, ResNet101, ResNet152
from models.r_resnet import RResNet18, RResNet34, RResNet50, RResNet101, RResNet152
from models.resnet_bibd import BResNet18, BResNet34, BResNet50, BResNet101, BResNet152

import time
import numpy as np

from experiment import Experiment
import pickle
from datetime import datetime


# Hyperparameters
BATCH_SIZE = 128
N_EPOCH = 30
print('Hyperparameters:')
print('    BATCH_SIZE: {:d}'.format(BATCH_SIZE))
print('    N_EPOCH: {:d}'.format(N_EPOCH))


print('ResNet experiments started.')

# Use start time for the filename of the pickled file
date_time = datetime.now().strftime("%Y%m%d_%H%M%S")


device = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Using PyTorch version:', torch.__version__, ' Device:', device)


print('Preparing the datasets...')
transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])
transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])
trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform_train)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform_test)
testloader = torch.utils.data.DataLoader(testset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)


print('Building the models...')
model_list = []
if torch.cuda.is_available():
    # ResNet models
    model_list.append(ResNet18().to(device))
    model_list.append(ResNet34().to(device))
    model_list.append(ResNet50().to(device))

    # B-ResNet models
    model_list.append(BResNet18().to(device))
    model_list.append(BResNet34().to(device))
    model_list.append(BResNet50().to(device))

    # R-ResNet models
    model_list.append(RResNet18().to(device))
    model_list.append(RResNet34().to(device))
    model_list.append(RResNet50().to(device))
else:
    print('CUDA is not available. Stopped.')
print('model_list: ')
for index, model in enumerate(model_list):
    print('   {:d}. {}'.format(index + 1, model.name))

experiment = Experiment(n_epoch=N_EPOCH)
for model in model_list:
    experiment.run_model(model, trainloader, testloader)


# Save all the experiment data
filename = 'resnet_experiments_{}.pkl'.format(date_time)
pickle.dump(experiment, open(filename, "wb"))
print('The Experiment instance experiment dumped to the file: {}'.format(filename))

print('ResNet experiments completed at {}'.format(datetime.now().strftime("%Y%m%d_%H%M%S")))