import re
from collections import OrderedDict

from gensim import corpora, models, similarities

import logging
import jieba

jieba.setLogLevel(logging.INFO)

DEFAULT_SIMILAR_THRESHOLD = 0.85


def merge(leader_playlist, *crowd_playlist_list, similar_threshold=DEFAULT_SIMILAR_THRESHOLD):
    if not leader_playlist:
        return

    # 以 leader playlist 中的频道名们建立索引
    index_texts = [segment_channel_name(channel[-2]) for channel in leader_playlist]
    sim_index = SimilarIndex(index_texts)
    merged_playlist = []

    def _merge(merged_leader_channel_idx_list):
        # 找出一个 base channel
        base_channel_index = None
        for i in range(len(leader_playlist)):
            if i not in merged_leader_channel_idx_list:
                base_channel_index = i
                break
        if base_channel_index is None:
            # 说明已经到底了
            # 下面将 crowd_playlist_list 中落单的 channels 放进最终结果的底部
            # 先将剩下的 channel 们按 group 整理好
            rest = OrderedDict()
            for crowd_playlist in crowd_playlist_list:
                for channel in crowd_playlist:
                    group_title = channel[-3]
                    group_channels = rest.get(group_title)
                    if not group_channels:
                        group_channels = []
                        rest[group_title] = group_channels
                    group_channels.append(channel)

            # 将分好组的 channels 放进最终结果的底部
            for group_channels in rest.values():
                merged_playlist.extend(group_channels)
            return

        base_channel = leader_playlist[base_channel_index]
        merged_playlist.append(base_channel)
        merged_leader_channel_idx_list.append(base_channel_index)

        # 先将 leader_playlist 中的与 base_channel 名字相同或相似 且 与 base_channel 同 group 的 channels 放进最终结果
        base_channel_and_siblings_indexs = [base_channel_index]
        sims = sim_index.find_sims(segment_channel_name(base_channel[-2]))
        for i, sim in enumerate(sims):
            if i not in merged_leader_channel_idx_list and sim >= similar_threshold:
                similar_to_base = leader_playlist[i]
                # 只有同一个分组 (group_title) 的才符合要求
                if similar_to_base[-3] == base_channel[-3]:
                    # 只有 url 不同时才添加
                    if similar_to_base[-1] != base_channel[-1]:
                        merged_playlist.append(similar_to_base)
                    base_channel_and_siblings_indexs.append(i)
                    merged_leader_channel_idx_list.append(i)

        # 再将 crowd_playlist 中与 base_channel 名字相同或相似的 channels 放进最终结果
        for crowd_playlist in crowd_playlist_list:

            def _eat_crowd_channel(index=0):
                if index >= len(crowd_playlist):
                    return

                    # for i, crowd_channel in enumerate(crowd_playlist):
                crowd_channel = crowd_playlist[index]
                sims = sim_index.find_sims(segment_channel_name(crowd_channel[-2]))

                # 判断 crowd_channel 是否与 base_channel_and_siblings_indexs 中的至少一个名字相似
                if [_i for _i in base_channel_and_siblings_indexs if sims[_i] >= similar_threshold]:
                    # 只有 url 不同时才添加
                    if crowd_channel[-1] != base_channel[-1]:
                        # 将其 group-title 改为和 base_channel 的一样
                        crowd_channel[-3] = base_channel[-3]
                        merged_playlist.append(crowd_channel)

                    crowd_playlist.pop(index)
                    # 吃掉了，下一位！
                    next_to_check = index
                else:
                    # 没吃掉，幸存了下来。有请下一位
                    next_to_check = index + 1

                _eat_crowd_channel(next_to_check)

            _eat_crowd_channel()

        # 找出下一个 base channel 及与它相似的 channel
        _merge(merged_leader_channel_idx_list)

    _merge([])

    return merged_playlist


# 分词
def segment_channel_name(name):
    name = name.lower()
    name = re.sub(r'福建(?=东南卫视)', '', name)
    name = re.sub(r'(?<=凤凰)卫视', '中文', name)

    stop_words = ['FHD'.lower(), 'HD'.lower(), 'SD'.lower(), '高清', '标清', '移动', '联通', '电信', '官方']
    regex = "|".join([r'\s+\d+', *[r'{}\s*\d*'.format(s) for s in stop_words]])
    name = re.sub(regex, '', name)

    words = jieba.cut(name)
    return [word for word in words if word.strip() != '']


class SimilarIndex:
    def __init__(self, index_texts):

        dictionary = corpora.Dictionary(index_texts)
        corpus = [dictionary.doc2bow(text) for text in index_texts]
        tfidf = models.TfidfModel(corpus)

        corpus_tfidf = tfidf[corpus]
        tfidf_index = similarities.MatrixSimilarity(corpus_tfidf)

        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary)
        lsi_vector = lsi[corpus_tfidf]
        lsi_index = similarities.MatrixSimilarity(lsi_vector)

        self.dictionary = dictionary
        self.tfidf = tfidf
        self.tfidf_index = tfidf_index
        self.lsi = lsi
        self.lsi_index = lsi_index

    def find_sims(self, words, model_type="tfidf"):
        """

        :param words:
        :param model_type: 'tfidf' | 'lsi'
        :return:
        """
        vec = self.dictionary.doc2bow(words)

        if model_type == 'tfidf':
            query_tfidf = self.tfidf[vec]
            return self.tfidf_index[query_tfidf]
        else:
            query_lsi = self.lsi[vec]
            return self.lsi_index[query_lsi]
