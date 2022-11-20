import torch
from torch.utils.data import Dataset

class UserSepDataset(Dataset):

    def __init__(self,
                 name,
                 sample_infos,
                 dataset_name='ASSISTments2009',
                 seq_zise=200,
                 ques_num=100,
                 pad_index=0
                 ):
        self._name = name  # train, val, test
        self._sample_infos = sample_infos  # list of (user_path, target_index)
        self._dataset_name = dataset_name
        self.seq_zise = seq_zise
        self.ques_num = ques_num
        self.pad_index = pad_index

    def get_sequence(self, sample):
        user_path, target_index = sample
        with open(user_path, 'r') as f:
            data = f.readlines()[1:]  # header exists
            data = data[:target_index + 1]
            user_data_length = len(data)

        if user_data_length > self.seq_zise + 1:
            data = data[-(self.seq_zise + 1):]
            pad_counts = 0
        else:
            pad_counts = self.seq_zise + 1 - user_data_length

        input_list = []
        for idx, line in enumerate(data):
            line = line.rstrip().split(',')
            tag_id = int(line[0])
            is_correct = int(line[1])

            if idx == len(data) - 1:
                last_is_correct = is_correct
                target_id = tag_id
            else:
                if is_correct:
                    input_list.append(tag_id)
                else:
                    input_list.append(tag_id + self.ques_num)

        paddings = [self.pad_index] * pad_counts
        input_list = paddings + input_list
        assert len(input_list) == self.seq_zise, "sequence size error"

        return {
            'label': torch.Tensor([last_is_correct]).long(),
            'input': torch.Tensor(input_list).long(),
            'target_id': torch.Tensor([target_id]).long()
        }

    def __repr__(self):
        return f'{self._name}: # of samples: {len(self._sample_infos)}'

    def __len__(self):
        return len(self._sample_infos)

    def __getitem__(self, index):
        return self.get_sequence(self._sample_infos[index])
