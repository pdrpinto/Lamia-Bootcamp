import torch
import plotly.graph_objs as go
import plotly.offline as pyo

# Criando um tensor tridimensional de valores aleatórios entre 0 e 1
tensor_3d = torch.rand((3, 3, 3))

# Listas para armazenar as coordenadas e valores dos elementos do tensor
x_vals, y_vals, z_vals, valores = [], [], [], []

# Percorrendo o tensor e armazenando os valores
for i in range(tensor_3d.shape[0]):
    for j in range(tensor_3d.shape[1]):
        for k in range(tensor_3d.shape[2]):
            x_vals.append(i)
            y_vals.append(j)
            z_vals.append(k)
            valores.append(tensor_3d[i, j, k].item())

# Criando um gráfico 3D com os valores do tensor
trace = go.Scatter3d(
    x=x_vals,
    y=y_vals,
    z=z_vals,
    mode='markers',
    marker=dict(
        size=8,
        color=valores,
        colorscale='Viridis',
        opacity=0.8
    )
)

layout = go.Layout(
    title='Visualização de Tensor 3D',
    margin=dict(l=0, r=0, b=0, t=40),
    scene=dict(
        xaxis_title='Dimensão X',
        yaxis_title='Dimensão Y',
        zaxis_title='Dimensão Z'
    )
)

fig = go.Figure(data=[trace], layout=layout)
pyo.iplot(fig)