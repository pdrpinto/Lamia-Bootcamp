import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from torchvision import datasets

device = 'cpu'
data_folder = ''
fmnist = datasets.FashionMNIST(data_folder, download=True, train=True)

tr_images = fmnist.data
tr_targets = fmnist.targets
val_fmnist = datasets.FashionMNIST(data_folder,
                                   download=True,
                                   train=False)

val_images = val_fmnist.data
val_targets = val_fmnist.targets

import albumentations as A
from albumentations.augmentations.geometric.transforms import ShiftScaleRotate

aug = A.Compose([
    ShiftScaleRotate(shift_limit_x=0.1, shift_limit_y=0, scale_limit=0, rotate_limit=0, p=1, border_mode=0),
])

# Extraindo imagens e rótulos
tr_images = fmnist.data
tr_targets = fmnist.targets

# Definição do dataset para Fashion MNIST
class FMNISTDataset(Dataset):
    def __init__(self, x, y, aug=None):
        self.x, self.y = x, y
        self.aug = aug
    
    def __getitem__(self, ix):
        x, y = self.x[ix], self.y[ix]
        return x, y
    
    def __len__(self):
        return len(self.x)
    
    def collate_fn(self, batch):
        ims, classes = list(zip(*batch))
        if self.aug:
            ims_np = np.array([tensor.numpy() for tensor in ims])  # Converte para NumPy
            ims = np.array([self.aug(image=img)['image'] for img in ims_np])  # Aplica transformações
        else:
            ims = np.array([tensor.numpy() for tensor in ims])  # Sem transformações
        
        # Converte para tensor e ajusta o formato
        ims = torch.tensor(ims, dtype=torch.float32).unsqueeze(1).to(device) / 255.
        classes = torch.tensor(classes).to(device)
        return ims, classes

# Definição do novo modelo de rede neural
class RedeNeuralClassificacao(nn.Module):
    def __init__(self, input_size=784, hidden_size=16, output_size=10):  # output_size=10 para FashionMNIST
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.leaky_relu = nn.LeakyReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, output_size)
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        x = x.view(x.size(0), -1)  # Redimensiona para (batch_size, 784)
        x = self.leaky_relu(self.fc1(x))
        x = self.leaky_relu(self.fc2(x))
        x = self.softmax(self.fc3(x))
        return x

# Criando um modelo
modelo = RedeNeuralClassificacao()

# Definindo a função de perda e otimizador
criterio = nn.CrossEntropyLoss()
otimizador = optim.Adam(modelo.parameters(), lr=0.01)

# Exibindo a estrutura do modelo
print(modelo)

# Função para obter os dados de treino e validação
def get_data():
    train = FMNISTDataset(tr_images, tr_targets, aug=aug)
    trn_dl = DataLoader(train, batch_size=64, collate_fn=train.collate_fn, shuffle=True)
    val = FMNISTDataset(val_images, val_targets)
    val_dl = DataLoader(val, batch_size=len(val_images), collate_fn=val.collate_fn, shuffle=True)
    return trn_dl, val_dl

# Obtendo os dados
trn_dl, val_dl = get_data()

# Função de treinamento
def treinar_modelo(modelo, criterio, otimizador, trn_dl, val_dl, epochs=10):
    for epoch in range(epochs):
        modelo.train()  # Coloca o modelo em modo de treino
        loss_acumulada = 0
        
        for imagens, labels in trn_dl:
            otimizador.zero_grad()  # Zera os gradientes acumulados
            saidas = modelo(imagens)  # Passa os dados pelo modelo
            loss = criterio(saidas, labels)  # Calcula a perda
            loss.backward()  # Calcula os gradientes
            otimizador.step()  # Atualiza os pesos
            loss_acumulada += loss.item()
        
        # Avaliação no conjunto de validação
        modelo.eval()
        with torch.no_grad():
            imagens_val, labels_val = next(iter(val_dl))
            saidas_val = modelo(imagens_val)
            loss_val = criterio(saidas_val, labels_val)
        
        print(f"Época {epoch+1}/{epochs} - Loss Treino: {loss_acumulada/len(trn_dl):.4f}, Loss Validação: {loss_val.item():.4f}")

# Criando um modelo
modelo = RedeNeuralClassificacao().to(device)

# Definindo a função de perda e otimizador
criterio = nn.CrossEntropyLoss()
otimizador = optim.Adam(modelo.parameters(), lr=0.01)

# Treinando o modelo
treinar_modelo(modelo, criterio, otimizador, trn_dl, val_dl, epochs=10)