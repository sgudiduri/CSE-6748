import torch
from d2l import torch as d2l
from torch import nn
from contract_nli.model.decomposable_attention import DecomposableAttention
from sklearn.metrics import classification_report

class Predict():
    def __init__(self, embed_size, num_hiddens,
                  model_path="contract_nli/trained_model/model.pth",
                  vocab_path="contract_nli/trained_model/vocab.pth"):
      self.embed_size = embed_size
      self.num_hiddens = num_hiddens
      self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
      self.vocab = torch.load(vocab_path)
      self.model = DecomposableAttention(self.vocab, self.embed_size,self.num_hiddens)
      self.model.load_state_dict(torch.load(model_path)) 
      self.model.to(self.device)     
      self.model.eval()
      
    def make_single_prediction(self, premise, hypothesis):         
      premise = torch.tensor(self.vocab[premise], device=d2l.try_gpu())
      hypothesis = torch.tensor(self.vocab[hypothesis], device=d2l.try_gpu())
      label = torch.argmax(self.model([premise.reshape((1, -1)),
                           hypothesis.reshape((1, -1))]), dim=1)
      return 'Entailment' if label == 0 else 'Contradiction' if label == 1 \
            else 'neutral'

    def make_multiple_prediction(self, data):
      y_hat=[]
      for i in range(len(data)):
          y_hat.append(self.make_single_prediction(data.iloc[i, :]["premise"].split(), \
                                data.iloc[i, :]["hypotheis"].split()))
      
      return y_hat
    
    def make_multiple_prediction_with_classification_report(self, data):
      def change_label(x):
        if x == "Entailment":
          return 0
        elif x =="Contradiction":
          return 1
        else:
          return 2
      y_hat =self.make_multiple_prediction(data);
      y_hat_transformed = [change_label(x) for x in y_hat]
      labels = data["label"].values
      print(f"\n {classification_report(labels, y_hat_transformed, labels=[0,1,2])}")


    
