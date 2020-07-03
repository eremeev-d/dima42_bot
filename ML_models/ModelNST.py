# Import libs
import numpy as np 
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.models as models
import torchvision.transforms as transforms
import PIL
from PIL import Image
from Core.misc import init_random
import os

# Normalization Module
class Normalization(nn.Module):
    def __init__(self, normalization_mean, normalization_std):
        super(Normalization, self).__init__()
        self.mean = normalization_mean.view(-1, 1, 1)
        self.std = normalization_std.view(-1, 1, 1)

    def forward(self, X):
        return (X - self.mean) / self.std

# Conent Module
class ContentLayer(nn.Module):
    def __init__(self, content):
        super(ContentLayer, self).__init__()
        self.loss = 0
        self.content = content.detach()

    def forward(self, X):
        self.loss = F.mse_loss(X, self.content)
        return X

# Style Module
def gram_matrix(X):
    batch, c, h, w = X.size()
    assert batch == 1
    X = X.view(c, h*w)
    G = torch.mm(X, X.t())
    G = G.div(c*h*w)
    return G

class StyleLayer(nn.Module):
    def __init__(self, style):
        super(StyleLayer, self).__init__()
        self.loss = 0
        self.style = gram_matrix(style.detach())

    def forward(self, X):
        G = gram_matrix(X)
        self.loss = F.mse_loss(G, self.style)
        return X

# ModelNST Module
class ModelNST:
	def hook(self, module, input, output):
		self.hooks.append(output)

	def __init__(self, content_img, style_img):
		# Init device (give me cuda plz......)
		self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		print("Running on {}".format(self.device))
		# Save content and style images
		self.content_img = content_img
		self.style_img = style_img
		# Create base_model
		self.base_model = models.resnet18(pretrained=True).to(self.device)
		for param in self.base_model.parameters():
			param.requires_grad = False
		# Model creation
		self.model = nn.Sequential()
		self.content_loss = []
		self.style_loss = []
		self.hooks = []
		# Normalization
		self.normalization_mean = torch.FloatTensor([0.485, 0.456, 0.406]).to(self.device)
		self.normalization_std = torch.FloatTensor([0.229, 0.224, 0.225]).to(self.device)
		self.model.add_module("Normalization", Normalization(self.normalization_mean, self.normalization_std))
		# Inplace ReLU may cause some troubles
		self.base_model.layer1[-1].relu = nn.ReLU(inplace=False)
		self.base_model.layer2[-1].relu = nn.ReLU(inplace=False)
		self.base_model.layer3[-1].relu = nn.ReLU(inplace=False)
		self.base_model.layer4[-1].relu = nn.ReLU(inplace=False)
		# We need content and style values on these layers
		self.base_model.layer1[-1].register_forward_hook(self.hook)
		self.base_model.layer2[-1].register_forward_hook(self.hook)
		self.base_model.layer3[-1].register_forward_hook(self.hook)
		self.base_model.layer4[-1].register_forward_hook(self.hook)
		self.hooks = []
		self.base_model(style_img)
		style_1 = self.hooks[0]
		style_2 = self.hooks[1]
		style_3 = self.hooks[2]
		self.hooks = []
		self.base_model(content_img)
		content_4 = self.hooks[3] 
		# Add Style and Content Layers
		self.base_model.layer1.add_module("Style_1", StyleLayer(style_1))
		self.base_model.layer2.add_module("Style_2", StyleLayer(style_2))
		self.base_model.layer3.add_module("Style_3", StyleLayer(style_3))
		self.base_model.layer4.add_module("Content_4", ContentLayer(content_4))
		self.style_loss.append(self.base_model.layer1[-1])
		self.style_loss.append(self.base_model.layer2[-1])
		self.style_loss.append(self.base_model.layer3[-1])
		self.content_loss.append(self.base_model.layer4[-1])
		# Complete Model
		self.model.add_module("ResNet", self.base_model)

	def run_nst(self, nb_epoch = 20, alpha = 1, beta = 2*10**8):
		# Init input and optmizer
		Input = self.content_img.clone()
		Input.requires_grad = True
		optimizer = torch.optim.LBFGS([Input])
		init_random()
		# Train Cycle
		t = [0]
		while t[0] <= nb_epoch:
			# Closure function for optimizer
			def closure():
				Input.data.clamp_(0, 1)
				optimizer.zero_grad()
				self.model(Input)
				del self.hooks
				self.hooks = []
				L_content = 0
				for layer in self.content_loss:
					L_content += layer.loss
				L_style = 0
				for layer in self.style_loss:
					L_style += layer.loss
				L_content *= alpha
				L_style *= beta
				loss = L_content + L_style
				loss.backward()
				t[0] += 1
				print(t[0])
				return L_content + L_style
			optimizer.step(closure)
		Input.data.clamp_(0, 1)
		return Input	