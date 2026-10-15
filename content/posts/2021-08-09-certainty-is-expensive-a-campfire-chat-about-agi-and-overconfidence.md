---
title: "Certainty is Expensive: A Campfire Chat about AGI and Overconfidence"
date: 2021-08-09
---

<aside class="note" markdown="1">
This article was originally published on [Medium](https://medium.com/@jhvithamar/certainty-is-expensive-a-campfire-chat-about-agi-and-overconfidence-4bc1a4fdc8d5). It has been ported to my own site with Claude Code
</aside>

![Photo by Mike Erskine on Unsplash](/images/certainty-is-expensive-a-campfire-chat-a-1.jpg)
*Photo by [Mike Erskine](https://unsplash.com/@mikejerskine?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

A week ago I was sitting by a campfire in Sweden. It was late at night and we had been drinking more than a few beers. At one point the conversation turned to the future of artificial intelligence. As that is on my top-1 of topics I like to discuss, I was excited to say the least. Gradually, the conversation narrowed down to the time horizon of when human-level artificial general intelligence (from now on; AGI) would be reached.

Though I don’t possess [Kurzweil levels of optimism](https://futurism.com/kurzweil-claims-that-the-singularity-will-happen-by-2045), I view it as a real possibility that human-level AGI could be reached within the next 100 years. That made me a fervent techno-optimist in the context of this discussion.

The other people were (much) more skeptical. They saw discussion of AGI as close to science fiction and had a hard time imagining how such a thing could be developed any time soon. There was especially one of the participants, who were adamantly techno-skeptic. I will call him Marvin as a nod to [Marvin Minsky](https://en.wikipedia.org/wiki/Marvin_Minsky), whose book [“Perceptrons” ushered in an AI winter](https://en.wikipedia.org/wiki/AI_winter#The_abandonment_of_connectionism_in_1969). Our disagreement made for a pretty fun debate.

In the midst of the fun, one statement from Marvin turned my excitement into frustration. The statement was that “AGI surely won’t be developed anytime in the next long while, so why even bother?”. (The original quote was in Danish but I’ve done my best to retain the meaning). I tried any way that I could to convince him of the fatal flaws in that statement. However, as I was tired, tipsy and Marvin had the high-ground advantage on the [Dunning-Kruger](https://www.researchgate.net/figure/Graph-of-the-Dunning-Kruger-effect-on-the-confidence-of-medical-students-in-their_fig1_333561136) battlefield, I repeatedly failed and, ultimately, went to sleep. This post is my attempt at finally rebuking the statement.

First and foremost I will clarify with what part of the statement I have a problem. It is not that “AI […] won’t be developed anytime soon”. [Surveys of experts in the field](https://aiimpacts.org/muller-and-bostrom-ai-progress-poll/) show fierce disagreement about the timeline with estimates ranging from twenty years to thousands and even never. All of these positions have valid(ish) arguments and I don’t blame Marvin for being pessimistic.

My biggest problem is not even the “so why even bother”, though I strongly believe that thinking about how to create [beneficial AI](https://people.eecs.berkeley.edu/~russell/papers/russell-bbvabook17-pbai.pdf) is an extremely important question. Many brilliant people such as [Boström](https://en.wikipedia.org/wiki/Superintelligence:_Paths,_Dangers,_Strategies), [Yudkowsky](https://intelligence.org/2016/12/28/ai-alignment-why-its-hard-and-where-to-start/), [Russell](https://en.wikipedia.org/wiki/Human_Compatible#:~:text=Human%20Compatible%3A%20Artificial%20Intelligence%20and,surrounding%20future%20progress%20in%20AI.) and [Jade Leung](https://www.youtube.com/watch?v=5YR9YgPx_Uc) have argued persuasively that this problem is underappreciated and extremely important. Covering their arguments would be beyond the scope of this blog (but do please check the links out!). However, as Marvin’s time spent seriously reading about this topic could be measured in minutes, I can sympathize with his reasoning.

The part that made my blood boil was a single word, namely “surely”. The huge problem with surely is that it communicates certainty. There is nothing wrong with certainty as such. If you are are calculating the mass of an electron you can assert with confidence that it is [~9.1093837015×10^-31 kg](https://en.wikipedia.org/wiki/Electron). You can also be certain that the sun will rise in the east tomorrow, as it has for the last many billion years.

The problem arises when you either a) are dealing with an intrinsically uncertain topic or b) don’t have the enough knowledge of the field. Marvin’s statement suffered from both flaws.

Imagine rolling a fair six-sided die. Before looking at the result you confidently proclaim “the die is surely a five”. Now imagine for the sake of argument that you look and the die was actually a five. Was the statement correct? I would argue no. Unless you are some kind of omniscient physics god, there is no way of knowing a priori what the die would show up as. It might as well have been a six or a one. Instead, it would have been more correct to simply say “I don’t know what the die will show”.

Saying “I don’t know” is known in [Bayesian statistics](https://www.lesswrong.com/posts/XTXWPQSEgoMkAupKt/an-intuitive-explanation-of-bayes-s-theorem) as having a flat prior. This can be reasonable when you know that the domain is highly uncertain (such as rolling a die). Sometimes, however, you do actually know more. For example, if you know that the die is loaded so 5’s are double as likely to show up you should say “I’m 28.57% sure that it would be a five”. This is what is called an “informed prior”. A good Bayesian would also update their prior after every roll, as there is a probability that the die might be loaded.

One thing a good Bayesian will never do is to be absolutely certain. The technical reason (which is described beautifully in this [blog post](https://www.lesswrong.com/posts/QGkYCwyC7wTDyt3yT/0-and-1-are-not-probabilities)) is that you cannot update your prior if you have assigned an event a probability of either 0 or 1. In probability theory, these values create a kind of black hole from which there is no escape. In less technical terms, you are saying that no amount of evidence can ever change your mind.

In the case of the die it would mean that seeing that even the die was not a five wouldn’t change your mind. Normally, I would say that this kind of behavior is unrealistic. No one can *actually* claim to be 100% nothing-can-change-my-mind certain. However, after debating Marvin for a couple of hours, I’ve readjusted my prior.

What does this all of this talk about dice and good Bayesian reasoning have to do with the probability of AGI? Quite a lot. Though, the development of AGI is not quite as random as the outcome of a die, it extremely difficult to predict. AGI development is affected by a plethora of different factors including [computational resources](https://www.datanami.com/2021/03/12/the-chip-shortage-seems-to-be-impacting-ai-workloads-in-the-cloud/), [business motives](https://www.theguardian.com/books/2019/oct/04/shoshana-zuboff-surveillance-capitalism-assault-human-automomy-digital-privacy), [geopolitics](https://www.youtube.com/watch?v=qjcA3rYzo54) and the [climate](https://www.forbes.com/sites/robtoews/2020/06/17/deep-learnings-climate-change-problem/). Many of these factors might both hasten and delay the development in complex feedback loops. Thus, we are dealing with what the philosopher [Nassim Taleb](https://www.fooledbyrandomness.com/) calls [epistemic randomness](https://www.stat.berkeley.edu/~aldous/Real_World/ale_epi.html). We have so many unknowns (and unknown unknowns) that certainty becomes practically impossible.

Another factor that certainty of the arrival of AGI implausible is that the development is contingent on conceptual breakthroughs. Conceptual breakthroughs are ideas that abruptly accelerates the development of a field. They are notoriously hard to predict. The Nobel prize winning physicist, Ernest Rutherford, found this out the hard way when he proclaimed [“Anyone who expects a source of power from the transformation of these atoms is talking moonshine.”](https://quoteinvestigator.com/2018/11/26/moonshine/#:~:text=%E2%80%9CAnyone%20who%20expects%20a%20source,these%20atoms%20is%20talking%20moonshine.%E2%80%9D) A year later the Hungarian physicist Leo Szilard conceived of [nuclear fission reaction](https://en.wikipedia.org/wiki/Leo_Szilard#Recognition_and_remembrance).

When even Nobel prize winning physicists can be overconfident in their own field, we should be extra careful. Certainty is expensive. Rutherford paid the price by becoming the symbol of scientific hubris in books and blog posts on AGI. However, it is possible to make the price much more literal.

An easy way to make put a price on overconfidence is by transforming it into a bet. Here certainty becomes infinitely expensive. This is because of how certainty interacts with expected value. Imagine that I proposed the following bet to Marvin: if AGI isn’t accomplished in the next 100 years I pay him $1, but if it is he pays me $100k. The expected value for him is:

![](/images/certainty-is-expensive-a-campfire-chat-a-2.png)

Being rational (as Marvin of course is) he should take the bet. He should even take the bet if he had to pay me a million, or even a billion dollars. Because of his certainty the payoff is guaranteed to be positive.

From my perspective, the payoff looks quite different. Say, that I use the results from a [survey of AI experts by Emerj](https://emerj.com/ai-future-outlook/when-will-we-reach-the-singularity-a-timeline-consensus-from-ai-researchers/) as my probability distribution.

![Results from the Emerj survey](/images/certainty-is-expensive-a-campfire-chat-a-3.png)
*Results from the Emerj survey*

For our purposes “reaching the singularity” is a good enough (albeit, conservative) estimate of reaching AGI (if we assume a [fast takeoff](https://www.lesswrong.com/posts/tjH8XPxAnr6JRbh7k/hard-takeoff)). Looking at the numbers, there’s a 62% chance that I will win the bet, and a 38% change that I won’t. Doing the math (with a payout of $100k) this gives an expected value of $61,999.82. Not too bad for a couple hours worth of discussions.

When I proposed the bet to Marvin while battling our hangover with a cup of coffee, he was not quite keen. Though he was still certain to win the bet, he objected that he wouldn’t live to get the pay-out. Fair point. Luckily, we could easily circumvent the issue by transforming the bet into an [option](https://www.investopedia.com/terms/o/option.asp). This is the option I proposed: Every year when we meet up in Sweden, I will bring him a beer. When (or if) human-level AGI is reached, he will pay me $100k.

The expected payoff for me is slightly smaller (up to 80x the cost of a beer), but in the grand scheme of things it is still a highly profitable bet (from both of our perspectives; Marvin enjoys a good beer). It does, however, depend on exactly what is meant by “Human Level AGI”? That will be the topic of next years fireside discussion, but if you have any ideas do write me!
