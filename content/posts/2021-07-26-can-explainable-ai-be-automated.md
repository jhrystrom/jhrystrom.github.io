---
title: "Can Explainable AI be Automated?"
date: 2021-07-26
---

<aside class="note" markdown="1">
This article was originally published on [Medium](https://becominghuman.ai/can-explainable-ai-be-automated-1b4f09a9a0e7). It has been ported to my own site with Claude Code
</aside>

![Photo by Possessed Photography on Unsplash](/images/can-explainable-ai-be-automated-1.jpg)
*Photo by [Possessed Photography](https://unsplash.com/@possessedphotography?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

I recently fell in love with Explainable AI (XAI). XAI is a set of methods aimed at making increasingly complex machine learning (ML) models understandable by humans. XAI could help bridge the gap between AI and humans. That is very much needed as the gap is widening. Machine learning is proving incredibly successful in tackling problems from [cancer diagnostics](https://www.nature.com/articles/s41598-019-48995-4) to [fraud detection](https://marutitech.medium.com/how-machine-learning-is-enhancing-fraud-detection-694f3a2237f). However, the human users are left staring at a black box. Even us Data Scientist can have a hard — if not impossible — time explaining *why* our neural network behaves as it does.

Here XAI comes to the rescue. With clever techniques like [SHAP](https://github.com/slundberg/shap), [semantic dictionaries](https://distill.pub/2018/building-blocks/) and [dimensionality reduction](https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf) we can explain and visualize the models in a more human friendly manner. No matter whether you’re an experienced data scientist debugging a convolutional neural network or a social worker trying to help a citizen with the help of a model, you’ll have an easier time understanding and trusting it. This can hopefully help making AI empowering instead of baffling. Therefore I believe XAI will be a key piece in making AI [beneficial](https://people.eecs.berkeley.edu/~russell/papers/russell-bbvabook17-pbai.pdf).

As I started planning how I might shape my career a question started nagging me: Will XAI be automated?

The question was grounded in development towards increased automation in Machine Learning. Models are requiring fewer and fewer lines of code to build. I got to experience this myself when I took the legendary [Machine Learning course by Andrew Ng](https://www.coursera.org/learn/machine-learning). The first assignment was to build a linear regression from scratch including the gradient descent. It took me hours of trial and error (plus an excessive amount of googling) to get it to work. The hard work made the first linear regression in R look almost magical. Instead of many lines of functions, it was just “lm()”. And it didn’t stop there.

As I started doing data science consultancy I got increasingly fascinated by automatic machine learning or [AutoML](https://www.automl.org/automl/). AutoML aims to automate the machine learning workflows (which is not too surprising giving the name). One such framework is [H2O](https://www.h2o.ai/). With H2O you supply a data set, a task (such as regression or classification), and a resource constraint (e.g. 30 minutes of computing), and then it goes on and builds an often well-performing model. Gone are the days of tedious model selection and hyperparameter tuning.

## Trending AI Articles:

> [1. Why Corporate AI projects fail?](https://becominghuman.ai/why-corporate-ai-projects-fail-part-1-4-3b820041ab00)

> [2. How AI Will Power the Next Wave of Healthcare Innovation?](https://becominghuman.ai/how-ai-will-power-the-next-wave-of-healthcare-innovation-695a2196aae8)

> [3. Machine Learning by Using Regression Model](https://becominghuman.ai/machine-learning-by-using-regression-model-f0c7993a66c8)

> [4. Top Data Science Platforms in 2021 Other than Kaggle](https://becominghuman.ai/top-data-science-platforms-in-2021-other-than-kaggle-a1b4609c06b0)

Of course, AutoML hasn’t sent hordes of now unemployed data scientists to the nearest barista school. There is still much data work left from data wrangling to feature engineering. However, these are also getting automated with libraries such as [FeatureTools](https://github.com/alteryx/featuretools). It might only be a matter of time before the technical side of data science is automated away.

Will XAI be different? From a technical perspective, it might seem so. As new ideas are developed, awesome libraries make them easy to use. A great example of this is the [SHAP library](https://github.com/slundberg/shap). SHAP uses game-theoretical credit assignment to weigh features in terms of importance. In addition, it provides out-of-the-box visualizations that allow you to quickly get a glance of your model. All in all a great library that I recommend checking out!

Most of these libraries are designed for specific use cases. SHAP, for instance, deals with supervised models (which covers are a large percentage of use cases). Other libraries handle [unsupervised learning](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html) or [language models](https://github.com/interpretml/interpret-text). As ever more libraries mature one might imagine a super-meta library that handles all situations. Just input your model and some nifty logic will figure out the state-of-the-art XAI model for that domain. It might even automatically create an optimal visualization to present to the user. Thus, even the XAI engineers will be queuing up at the barista school.

This approach, unfortunately (or luckily, depending on who you ask) neglects one essential problem: the user. Communication is not a one-way street. There is no such thing as universally good explanations. People learn and understand differently. A SHAP-value of -10.5 for “LTM_rev_delta” might be clear as day for the data scientist who builds the model. Not so much for the customer service agent calling the customer possibly about to unsubscribe (or “churn” as it is often known).

In addition to the personality of the user, the context is also key. A customer retention agent preparing a presentation on the general characteristics of churners needs help exploring. He has time to explore the information slowly and potentially scrutinize and compare different cases. That luxury has vanished when he is dialing a potential churner to convince her to stay.

These examples highlight the essence of XAI: understanding. Many AI systems aim to help people make better decisions. And understanding is crucial for making good decisions. If the customer retention agent understands that the model was focusing on the fact that the customer just canceled her newsletter subscription, he can ask her why she unsubscribed. He can then plan potential strategies based on her response — before she even picks up the phone! This allows the agent to be much more efficient than if he just knew she was a possible churner.

The role of understanding is why I believe AutoXAI is far in the future. While traditional ML has a clear mathematical objective (minimize the cost function), there is no formula for understanding. When we explain something to someone we are essentially trying to manipulate one of the most complex objects in the known universe, namely the human brain. We only succeed in this daunting task because we are lucky enough to also possess this magical lump of fat.

That is not to say that we will never develop AutoXAI. One might imagine a model trained on tons of behavioral (or brain!) data that adaptively tailors explanations to specific users in specific contexts. It know how to present the exact right kind of information in the exact right way to maximize understanding. Though such a system would be awesome (in the literal sense), we would face much bigger issues than retaining customers (such as making sure it doesn’t develop a too keen interest in making paper clips!). Until then it is important to remember that XAI is about helping the user understand the system. And that this challenge requires both technical solutions and a bit of empathy.
