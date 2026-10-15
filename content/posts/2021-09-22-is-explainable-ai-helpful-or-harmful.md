---
title: "Is Explainable AI Helpful or Harmful?"
date: 2021-09-22
---

<aside class="note" markdown="1">
This article was originally published on [Medium](https://medium.com/@jhvithamar/is-explainable-ai-helpful-or-harmful-713fcca061de). It has been ported to my own site with Claude Code
</aside>

![Photo by Rock'n Roll Monkey on Unsplash](/images/is-explainable-ai-helpful-or-harmful-1.jpg)
*Photo by [Rock'n Roll Monkey](https://unsplash.com/@rocknrollmonkey?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

“Explainable AI (XAI) is a set of methods aimed at making increasingly complex Machine Learning (ML) models understandable by humans”. That’s how I defined XAI in a [previous post](/posts/2021/07/can-explainable-ai-be-automated/) where I argued that XAI is both important and extremely difficult to automate. In a nutshell, XAI is crucial for building trust and understanding with (often non-technical) end-users. This empowers the user to actively use and adapt the system. The goal is to create ML-systems with maximal benefits and minimal accidental misuse.

I got a bunch of interesting feedback and comments on the post (thank you!). One that stuck with me was from an incredibly smart senior data scientist. He said that he didn’t believe in XAI because it inevitably distorts the underlying model. He argues that one should instead really on [intrinsically interpretable models](https://christophm.github.io/interpretable-ml-book/taxonomy-of-interpretability-methods.html), i.e. models that are interpretable as is to data scientist.

It is an excellent point. Though I disagree with the premises, namely that intrinsically interpretable models a) always are feasible and b) are interpretable to end-users, it does raise an incredibly important question: Is XAI actually harmful? And if so, in what sense?

## XAI Gone Wrong: A Fictional Story

To investigate this question I’ll use the example of the fictional product ApplicationScanner. ApplicationScanner is a solution by the AI company El Goog that scans job-applications and — with the help of some AI-magic- selects the most promising candidates. Under the hood it creates the recommendations based on [transformer-based document embeddings](https://github.com/flairNLP/flair/blob/master/resources/docs/TUTORIAL_5_DOCUMENT_EMBEDDINGS.md#transformerdocumentembeddings) and a vast database of previous successful applicants. The team chose transformers because it gave them a tremendous performance boost over simpler techniques such as [Bag of Words](https://en.wikipedia.org/wiki/Bag-of-words_model) or [TF-IDF](https://monkeylearn.com/blog/what-is-tf-idf/).

The increase in performance comes at a cost of interpretability. Though, the performance metrics are great it is impossible to say how the algorithms decides. To remedy this, the ApplicationScanner data scientists develop a post-hoc XAI-module that explains the predictions using human-understandable features. Instead of just outputting a “SuccessScore” with no explanation, the model now adds a rating using categories such as “Experience” and “Ingenuity”. This boosts trust to ApplicationScanner and the entire team goes off celebrating.

There is, however, a problem. A huge problem. A curious data scientist tries to understand these post-hoc features. She stumbles upon one with extremely high predictive power called “Education Quality”, a feature that judges were people went to school. Intuitively this seems like a valid feature. But after a bit of digging the data scientist realizes that “Education Quality” actually focuses on the ethnic composition of different schools! Schools with more non-white students consistently score lower, regardless of actual academic output. Instead of making objective assessments, ApplicationScanner is yet another unfortunate example of [AI propagating bias](https://time.com/5520558/artificial-intelligence-racial-gender-bias/). She immediately contacts the rest of the team and they begin the rough process of de-biasing the data set.

## Different kinds of Black Boxes

Not every team is fortunate enough to have their problems caught by a curious data scientist. Errors and biases in model can generate shit-storms that can seriously harm users, customers and the companies brands as [countless examples illustrate](https://github.com/daviddao/awful-ai). Therefore, it is crucial to understand when and how these systems go wrong.

A central piece of the puzzle is to distinguish between different kinds of black boxes. As argued by the EU-funded paper [“Artificial Intelligence: From Ethics to Policy”](<https://www.europarl.europa.eu/RegData/etudes/STUD/2020/641507/EPRS_STU(2020)641507_EN.pdf>) there are three different kinds of black boxes: algorithmic black boxes, commercial black boxes, and end-user black boxes.

![The three kinds of Machine Learning black boxes explained (following Wynsberghe, 2020 )](/images/is-explainable-ai-helpful-or-harmful-2.png)
*The three kinds of Machine Learning black boxes explained (following [Wynsberghe, 2020](<https://www.europarl.europa.eu/RegData/etudes/STUD/2020/641507/EPRS_STU(2020)641507_EN.pdf>))*

Algorithmic black boxes are what most people normally think of when talking about black boxes; models that are intrinsically obscure even to experts. The most prevalent algorithmic black boxes today are different kinds of neural networks that perform [excellently in complicated scenario](https://deepmind.com/research?filters=%7B%22tags%22:%5B%22Deep%20learning%22%5D%7D) while remaining inscrutable.

Commercial black boxes are algorithms where the inner workings are intentionally obscured to preserve commercial interests. This counts Google’s search algorithm that is freely available to use but highly secretive. Many companies, understandably, choose commercial black boxes to protect intellectual property that often is their competitive advantage.

Last but not least, is end-user black boxes. These are models that are understood by experts (like data scientists) while being black boxes to non-technical end-users. This includes a wide array decision-support tools (like ApplicationScanner before the XAI-module). End-user black boxes are important but often neglected but the reasons why will be the topic of a future post.

The three boxes provide a framework for understanding ML-systems. Instead of simply talking about “black boxes” it allows us to be specific about *what kind of* black box we are dealing with. This allows for a more nuanced and productive discussion of XAI.

Using this framework gives new understanding to the problems of ApplicationScanner. The XAI-module only addressed the end-user black box while the underlying still was an algorithmic black box. This mismatch created a false sense of trustworthiness as the model *seemed* understandable without *actually* being understandable.

## Risks of XAI (and the lack hereof)

This kind of misalignment can exaggerate the risks of black box systems. If a system seems trustworthy users are more [likely to rely on it](https://www.aaai.org/ocs/index.php/SSS/SSS17/paper/viewPaper/15372). If the decision is about approving a loan hidden biases can have catastrophic consequences for the denied applicants. If the decision is about armed retaliation the consequences can be [catastrophic for humanity](https://futureoflife.org/open-letter-autonomous-weapons/).

However, not having XAI could also lead to adverse consequences. Imagine an algorithmically clear prediction model (say, a logistic regression) being used for loan applications. The data scientists have a good understand of how it works and don’t bother creating any end-user XAI-module. Instead they just hand over the model to the loan officers, assure them the model is trustworthy and go out to celebrate.

This scenario might also create a false sense of trustworthiness. If the loan officers trust but don’t understand the predictions they might blindly follow the advice of the model. They might therefore be less likely to notice and report subtle (and not so subtle) errors such as [train-test distributional shifts](https://towardsdatascience.com/understanding-dataset-shift-f2a5a262a766). This might lead to the same bad decisions as well as greatly reducing the quality of the feedback for the data scientists. All of this rests on the assumption that end-users even want to use models they don’t trust, which they might [reasonably want to avoid](https://en.wikipedia.org/wiki/Weapons_of_Math_Destruction).

## Conclusion and the path forward for XAI

Instead of being point blanch for-or-against XAI, we should carefully and explicitly consider which kind of black box a solution addresses. If an XAI-solution is aimed at end-users it is crucial that it is aligned with the underlying model. If the underlying model is algorithmically opaque the XAI-solution should reflect the uncertainty. The less algorithmically opaque the underlying model is the more clear the end-user focused solution should be.

At the heart of this is the human task of designing systems with the user in mind. This way we can create trustworthy systems were no box is left unacceptably black.
