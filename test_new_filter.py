import parser
import string
import argparse

import torch
import torch.backends.cudnn as cudnn
import torch.utils.data
import torch.nn.functional as F

from utils import AttnLabelConverter
from model import Model
from torchvision import transforms
from Parser import parser
from PIL import Image
from new_filter import filter
from filter import filterImage
from datetime import date, datetime


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def log(to_print, verbose=True):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("./log.txt", 'a') as f:
        f.write("[%s] : %s\n" % (timestamp, to_print))
    if verbose:
        print("[%s] : %s" % (timestamp, to_print))

class recognition:
    def __init__(self):
        self.opt = parser.parse_args()

        if self.opt.sensitive:
            self.opt.character = string.printable[:6]

        cudnn.benchmark = True
        cudnn.deterministic = True
        self.opt.num_gpu = torch.cuda.device_count()
        # self.recognition(self.opt)

        # load model
        self.converter = AttnLabelConverter(self.opt.character)
        self.opt.num_class = len(self.converter.character)
        self.model = Model(self.opt)

        self.model = torch.nn.DataParallel(self.model).to(device)
        print("loading pretrained model from %s" % self.opt.saved_model)
        self.model.load_state_dict(
            torch.load(self.opt.saved_model, map_location=device)
        )

        print("model loaded")

        self.model.eval()

    def recognition(self, im):
        confidence_score = 0

        # img = filterImage(im)
        img = filter(im)
        transform = transforms.Compose(
            [transforms.ToTensor()]
            # [transforms.CenterCrop([32, 100]), transforms.ToTensor()]
        )
        img_tensor = transform(img)[0].unsqueeze(0).unsqueeze(0)
        # print(img_tensor, img_tensor.shape)

        with torch.no_grad():
            batch_size = 1
            image = img_tensor.to(device)
            # For max length prediction
            length_for_pred = torch.IntTensor(
                [self.opt.batch_max_length] * batch_size
            ).to(device)
            text_for_pred = (
                torch.LongTensor(batch_size, self.opt.batch_max_length + 1)
                .fill_(0)
                .to(device)
            )
            preds = self.model(image, text_for_pred, is_train=False)

            # select max probabilty (greedy decoding) then decode index to character
            _, preds_index = preds.max(2)
            preds_str = self.converter.decode(preds_index, length_for_pred)

            preds_prob = F.softmax(preds, dim=2)
            preds_max_prob, _ = preds_prob.max(dim=2)

            if "Attn" in self.opt.Prediction:
                pred_EOS = preds_str[0].find("[s]")
                pred = preds_str[0][
                    :pred_EOS
                ]  # prune after "end of sentence" token ([s])
                pred_max_prob = preds_max_prob[0][:pred_EOS]

            # calculate confidence score (= multiply of pred_max_prob)
            confidence_score = pred_max_prob.cumprod(dim=0)[-1]

            print(f"{pred:25s}\t{confidence_score:0.4f}")

            return pred, confidence_score

if __name__ == "__main__":
    recon = recognition()
    for i in range(100):
        img = Image.open(f"./Screenshots/validation{i}.png")
        validation_code, confidence = recon.recognition(img)
        log(f"{i} : confidence{confidence:0.4f} , validation_code: {validation_code}")

