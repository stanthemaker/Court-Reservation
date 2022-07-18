import parser
import string
import argparse
import pytesseract
import torch
import torch.backends.cudnn as cudnn
import torch.utils.data
import torch.nn.functional as F

from utils import AttnLabelConverter
from model import Model
from torchvision import transforms
from Parser import parser
from PIL import Image
from filter import filterImage

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# def recognition(opt):
#     converter = AttnLabelConverter(opt.character)
#     opt.num_class = len(converter.character)
#     model = Model(opt)
#     print(
#         "model input parameters",
#         opt.imgH,
#         opt.imgW,
#         opt.num_fiducial,
#         opt.input_channel,
#         opt.output_channel,
#         opt.hidden_size,
#         opt.num_class,
#         opt.batch_max_length,
#         opt.Transformation,
#         opt.FeatureExtraction,
#         opt.SequenceModeling,
#         opt.Prediction,
#     )

#     model = torch.nn.DataParallel(model).to(device)
#     # load model
#     print("loading pretrained model from %s" % opt.saved_model)
#     model.load_state_dict(torch.load(opt.saved_model, map_location=device))

#     confidence_score = 0
#     idx = 0
#     while confidence_score < 0.96:
#         img_path = "./img.png"
#         response = requests.get(url, stream=True)
#         if response.status_code == 200:
#             with open(img_path, "wb") as f:
#                 response.raw.decode_content = True
#                 shutil.copyfileobj(response.raw, f)
#             print("image saved")

#         filterImage(img_path)
#         transform = transforms.Compose(
#             [transforms.CenterCrop([32, 100]), transforms.ToTensor()]
#         )
#         img = Image.open("./filtered.png").convert("LA")
#         # img.show()
#         img_tensor = transform(img)[0].unsqueeze(0).unsqueeze(0)
#         # print(img_tensor, img_tensor.shape)

#         model.eval()

#         with torch.no_grad():
#             batch_size = 1
#             image = img_tensor.to(device)
#             # For max length prediction
#             length_for_pred = torch.IntTensor([opt.batch_max_length] * batch_size).to(
#                 device
#             )
#             text_for_pred = (
#                 torch.LongTensor(batch_size, opt.batch_max_length + 1)
#                 .fill_(0)
#                 .to(device)
#             )
#             preds = model(image, text_for_pred, is_train=False)

#             # select max probabilty (greedy decoding) then decode index to character
#             _, preds_index = preds.max(2)
#             preds_str = converter.decode(preds_index, length_for_pred)

#             preds_prob = F.softmax(preds, dim=2)
#             preds_max_prob, _ = preds_prob.max(dim=2)

#             if "Attn" in opt.Prediction:
#                 pred_EOS = preds_str[0].find("[s]")
#                 pred = preds_str[0][
#                     :pred_EOS
#                 ]  # prune after "end of sentence" token ([s])
#                 pred_max_prob = preds_max_prob[0][:pred_EOS]

#             # calculate confidence score (= multiply of pred_max_prob)
#             confidence_score = pred_max_prob.cumprod(dim=0)[-1]

#             print(f"{img_path:25s}\t{pred:25s}\t{confidence_score:0.4f}")
#             idx += 1


# if __name__ == "__main__":
#     opt = parser.parse_args()

#     """ vocab / character number configuration """
#     if opt.sensitive:
#         # same with ASTER setting (use 94 char).
#         opt.character = string.printable[:-6]

#     cudnn.benchmark = True
#     cudnn.deterministic = True
#     opt.num_gpu = torch.cuda.device_count()
#     recognition(opt)


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

        img = filterImage(im)
        number = pytesseract.image_to_string(img)
        return number
        
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
