# Copyright 2020 The HuggingFace Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Google BLEU (aka GLEU) metric. """

from typing import Dict, List

from nltk.translate import gleu_score

import datasets
from datasets import MetricInfo


_CITATION = """\
@misc{wu2016googles,
      title={Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation},
      author={Yonghui Wu and Mike Schuster and Zhifeng Chen and Quoc V. Le and Mohammad Norouzi and Wolfgang Macherey
              and Maxim Krikun and Yuan Cao and Qin Gao and Klaus Macherey and Jeff Klingner and Apurva Shah and Melvin
              Johnson and Xiaobing Liu and Łukasz Kaiser and Stephan Gouws and Yoshikiyo Kato and Taku Kudo and Hideto
              Kazawa and Keith Stevens and George Kurian and Nishant Patil and Wei Wang and Cliff Young and
              Jason Smith and Jason Riesa and Alex Rudnick and Oriol Vinyals and Greg Corrado and Macduff Hughes
              and Jeffrey Dean},
      year={2016},
      eprint={1609.08144},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
"""

_DESCRIPTION = """\
The BLEU score has some undesirable properties when used for single
sentences, as it was designed to be a corpus measure. We therefore
use a slightly different score for our RL experiments which we call
the 'GLEU score'. For the GLEU score, we record all sub-sequences of
1, 2, 3 or 4 tokens in output and target sequence (n-grams). We then
compute a recall, which is the ratio of the number of matching n-grams
to the number of total n-grams in the target (ground truth) sequence,
and a precision, which is the ratio of the number of matching n-grams
to the number of total n-grams in the generated output sequence. Then
GLEU score is simply the minimum of recall and precision. This GLEU
score's range is always between 0 (no matches) and 1 (all match) and
it is symmetrical when switching output and target. According to
our experiments, GLEU score correlates quite well with the BLEU
metric on a corpus level but does not have its drawbacks for our per
sentence reward objective.
"""

_KWARGS_DESCRIPTION = """\
Computes corpus-level Google BLEU (GLEU) score of translated segments against one or more references.
Instead of averaging the sentence level GLEU scores (i.e. macro-average precision), Wu et al. (2016) sum up the matching
tokens and the max of hypothesis and reference tokens for each sentence, then compute using the aggregate values.

Args:
    predictions (list of str): list of translations to score.
        Each translation should be tokenized into a list of tokens.
    references (list of list of str): list of lists of references for each translation.
        Each reference should be tokenized into a list of tokens.
    sentence_level (boolean): If True, calculates google bleu scores at the sentence level,
        and returns a list of scores. If False, calculates score on the corpus level,
        returning a single score. Defaults to True.
    min_len (int): The minimum order of n-gram this function should extract. Defaults to 1.
    max_len (int): The maximum order of n-gram this function should extract. Defaults to 4.

Returns:
    'google_bleu': google_bleu score

Examples:
    Example 1:
        >>> hyp1 = ['It', 'is', 'a', 'guide', 'to', 'action', 'which',
        ...         'ensures', 'that', 'the', 'rubber', 'duck', 'always',
        ...         'disobeys', 'the', 'commands', 'of', 'the', 'cat']
        >>> ref1a = ['It', 'is', 'the', 'guiding', 'principle', 'which',
        ...          'guarantees', 'the', 'rubber', 'duck', 'forces', 'never',
        ...          'being', 'under', 'the', 'command', 'of', 'the', 'cat']

        >>> hyp2 = ['he', 'read', 'the', 'book', 'because', 'he', 'was',
        ...         'interested', 'in', 'world', 'history']
        >>> ref2a = ['he', 'was', 'interested', 'in', 'world', 'history',
        ...          'because', 'he', 'read', 'the', 'book']

        >>> list_of_references = [[ref1a], [ref2a]]
        >>> hypotheses = [hyp1, hyp2]
        >>> google_bleu = datasets.load_metric("google_bleu")
        >>> results_sentence_level = google_bleu.compute(predictions=hypotheses, references=list_of_references)
        >>> results_corpus_level = google_bleu.compute(predictions=hypotheses, references=list_of_references, sentence_level=False)
        >>> print([round(score, 2) for score in results_sentence_level["google_bleu"]])
        [0.24, 0.79]
        >>> print(round(results_corpus_level["google_bleu"], 2))
        0.44

    Example 2:
        >>> hyp1 = ['It', 'is', 'a', 'guide', 'to', 'action', 'which',
        ...         'ensures', 'that', 'the', 'rubber', 'duck', 'always',
        ...         'disobeys', 'the', 'commands', 'of', 'the', 'cat']
        >>> ref1a = ['It', 'is', 'the', 'guiding', 'principle', 'which',
        ...          'guarantees', 'the', 'rubber', 'duck', 'forces', 'never',
        ...          'being', 'under', 'the', 'command', 'of', 'the', 'cat']
        >>> ref1b = ['It', 'is', 'a', 'guide', 'to', 'action', 'that',
        ...          'ensures', 'that', 'the', 'rubber', 'duck', 'will', 'never',
        ...          'heed', 'the', 'cat', 'commands']
        >>> ref1c = ['It', 'is', 'the', 'practical', 'guide', 'for', 'the',
        ...          'rubber', 'duck', 'army', 'never', 'to', 'heed', 'the', 'directions',
        ...          'of', 'the', 'cat']

        >>> hyp2 = ['he', 'read', 'the', 'book', 'because', 'he', 'was',
        ...         'interested', 'in', 'world', 'history']
        >>> ref2a = ['he', 'was', 'interested', 'in', 'world', 'history',
        ...          'because', 'he', 'read', 'the', 'book']

        >>> list_of_references = [[ref1a, ref1b, ref1c], [ref2a]]
        >>> hypotheses = [hyp1, hyp2]
        >>> google_bleu = datasets.load_metric("google_bleu")
        >>> results_sentence_level = google_bleu.compute(predictions=hypotheses, references=list_of_references)
        >>> results_corpus_level = google_bleu.compute(predictions=hypotheses, references=list_of_references, sentence_level=False)
        >>> print([round(score, 2) for score in results_sentence_level["google_bleu"]])
        [0.51, 0.79]
        >>> print(round(results_corpus_level["google_bleu"], 2))
        0.61

    Example 3:
        >>> hyp1 = ['It', 'is', 'a', 'guide', 'to', 'action', 'which',
        ...         'ensures', 'that', 'the', 'rubber', 'duck', 'always',
        ...         'disobeys', 'the', 'commands', 'of', 'the', 'cat']
        >>> ref1a = ['It', 'is', 'the', 'guiding', 'principle', 'which',
        ...          'guarantees', 'the', 'rubber', 'duck', 'forces', 'never',
        ...          'being', 'under', 'the', 'command', 'of', 'the', 'cat']
        >>> ref1b = ['It', 'is', 'a', 'guide', 'to', 'action', 'that',
        ...          'ensures', 'that', 'the', 'rubber', 'duck', 'will', 'never',
        ...          'heed', 'the', 'cat', 'commands']
        >>> ref1c = ['It', 'is', 'the', 'practical', 'guide', 'for', 'the',
        ...          'rubber', 'duck', 'army', 'never', 'to', 'heed', 'the', 'directions',
        ...          'of', 'the', 'cat']

        >>> hyp2 = ['he', 'read', 'the', 'book', 'because', 'he', 'was',
        ...         'interested', 'in', 'world', 'history']
        >>> ref2a = ['he', 'was', 'interested', 'in', 'world', 'history',
        ...          'because', 'he', 'read', 'the', 'book']

        >>> list_of_references = [[ref1a, ref1b, ref1c], [ref2a]]
        >>> hypotheses = [hyp1, hyp2]
        >>> google_bleu = datasets.load_metric("google_bleu")
        >>> results_sentence_level_level = google_bleu.compute(predictions=hypotheses, references=list_of_references, min_len=2)
        >>> results_corpus_level = google_bleu.compute(predictions=hypotheses, references=list_of_references, min_len=2, sentence_level=False)
        >>> print([round(score, 2) for score in results_sentence_level["google_bleu"]])
        [0.43, 0.70]
        >>> print(round(results_corpus_level["google_bleu"], 2))
        0.53

    Example 4:
        >>> hyp1 = ['It', 'is', 'a', 'guide', 'to', 'action', 'which',
        ...         'ensures', 'that', 'the', 'rubber', 'duck', 'always',
        ...         'disobeys', 'the', 'commands', 'of', 'the', 'cat']
        >>> ref1a = ['It', 'is', 'the', 'guiding', 'principle', 'which',
        ...          'guarantees', 'the', 'rubber', 'duck', 'forces', 'never',
        ...          'being', 'under', 'the', 'command', 'of', 'the', 'cat']
        >>> ref1b = ['It', 'is', 'a', 'guide', 'to', 'action', 'that',
        ...          'ensures', 'that', 'the', 'rubber', 'duck', 'will', 'never',
        ...          'heed', 'the', 'cat', 'commands']
        >>> ref1c = ['It', 'is', 'the', 'practical', 'guide', 'for', 'the',
        ...          'rubber', 'duck', 'army', 'never', 'to', 'heed', 'the', 'directions',
        ...          'of', 'the', 'cat']

        >>> hyp2 = ['he', 'read', 'the', 'book', 'because', 'he', 'was',
        ...         'interested', 'in', 'world', 'history']
        >>> ref2a = ['he', 'was', 'interested', 'in', 'world', 'history',
        ...          'because', 'he', 'read', 'the', 'book']

        >>> list_of_references = [[ref1a, ref1b, ref1c], [ref2a]]
        >>> hypotheses = [hyp1, hyp2]
        >>> google_bleu = datasets.load_metric("google_bleu")
        >>> results_sentence_level = google_bleu.compute(predictions=hypotheses,references=list_of_references, min_len=2, max_len=6)
        >>> results_corpus_level = google_bleu.compute(predictions=hypotheses,references=list_of_references, min_len=2, max_len=6, sentence_level=False)
        >>> print([round(score, 2) for score in results_sentence_level["google_bleu"]])
        [0.33, 0.55]
        >>> print(round(results_corpus_level["google_bleu"], 2))
        0.4
"""


@datasets.utils.file_utils.add_start_docstrings(_DESCRIPTION, _KWARGS_DESCRIPTION)
class GoogleBleu(datasets.Metric):
    def _info(self) -> MetricInfo:
        return datasets.MetricInfo(
            description=_DESCRIPTION,
            citation=_CITATION,
            inputs_description=_KWARGS_DESCRIPTION,
            features=datasets.Features(
                {
                    "predictions": datasets.Sequence(datasets.Value("string", id="token"), id="sequence"),
                    "references": datasets.Sequence(
                        datasets.Sequence(datasets.Value("string", id="token"), id="sequence"), id="references"
                    ),
                }
            ),
        )

    def _compute(
        self,
        predictions: List[List[List[str]]],
        references: List[List[str]],
        sentence_level: bool = True,
        min_len: int = 1,
        max_len: int = 4,
    ) -> Dict[str, float]:
        if sentence_level:
            sentence_scores = []
            for pred, refs in zip(predictions, references):
                sentence_scores.append(gleu_score.sentence_gleu(references=refs, hypothesis=pred, min_len=min_len, max_len=max_len))
            return {"google_bleu": sentence_scores}
        else:
            return {
                "google_bleu": gleu_score.corpus_gleu(
                    list_of_references=references, hypotheses=predictions, min_len=min_len, max_len=max_len
                )
            }
