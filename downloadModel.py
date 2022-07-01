import gdown

url = 'https://drive.google.com/u/2/uc?id=1MtzZ9HDfaa9205bhz7yWBQVZaAZuVvwb&export=download'
output = 'TPS-ResNet-BiLSTM-Attn.pth'
gdown.download(url, output)
