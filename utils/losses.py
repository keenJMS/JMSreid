from __future__ import absolute_import
import sys

import torch
from torch import nn
import numpy as np

class TripletLoss(nn.Module):
    def __init__(self,margin=0.3):
        super(TripletLoss, self).__init__()
        self.margin = margin
        self.ranking_loss = nn.MarginRankingLoss(margin=margin)

    def forward(self,inputs,targets):
        """
        Args:
            inputs: feature matrix with shape (batch_size, feat_dim)
            targets: ground truth labels with shape (num_classes)
        """
        n=inputs.size(0)
        dist=torch.pow(inputs,2).sum(dim=1,keepdim=True).expand(n,n)\
            +torch.pow(inputs,2).sum(dim=1,keepdim=True).expand(n,n).t()
        dist=dist.addmm_(1,-2,inputs,inputs.t())
        dist=dist.clamp(min=1e-12).sqrt()
        mask=targets.expand(n,n).eq(targets.expand(n,n).t())
        dist_ap=[]
        dist_an=[]
        for i in range(n):
            dist_ap.append(dist[i][mask[i]].max().unsqueeze(0))
            dist_an.append(dist[i][mask[i]==False].min().unsqueeze(0))
        dist_ap=torch.cat(dist_ap)
        dist_an=torch.cat(dist_an)
        # Compute ranking hinge loss
        y = torch.ones_like(dist_an)
        loss = self.ranking_loss(dist_an, dist_ap, y)
        return loss

if __name__=='__main__':
    target=[1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4]
    target=torch.Tensor(target)
    features=torch.Tensor(16,2048)
    lossf=TripletLoss()
    loss=lossf.forward(features,target)
    pass