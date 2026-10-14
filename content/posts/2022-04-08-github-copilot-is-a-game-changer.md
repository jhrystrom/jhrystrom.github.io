---
title: "GitHub Copilot is a Game Changer"
date: 2022-04-08
permalink: /posts/2022/04/github-copilot-is-a-game-changer/
---

<aside class="note" markdown="1">
I published this post after a few weeks of playing around with the original GitHub co-pilot in [April(!) of 2022(!!)](https://medium.com/codex/github-copilot-is-a-game-changer-cd0a2bbe6de8). While much has changed in the world of coding agents since (remember this is ~7 months before ChatGPT and ~3.5 years before Claude Code), I think it holds up quite well.
</aside>

![Photo by Avel Chuklanov on Unsplash](/images/copilot-header.jpg)
*Photo by [Avel Chuklanov](https://unsplash.com/@chuklanov?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com/?utm_source=medium&utm_medium=referral)*

Microsoft recently opened the beta for [Github Copilot](https://copilot.github.com/), a powerful code-completion tool based on [OpenAI’s codex](https://openai.com/blog/openai-codex/). I was one of the lucky not-so few that got access about a week ago, and I was impressed. Extremely impressed. Also a little bit scared. But mainly impressed.

As I was scrolling through my feed I could see many friends and colleagues writing about it, who weren’t quite as impressed as me. They saw it more as a “fun tool” that nevertheless had “trouble writing complicated code”. In this article, I will argue that Copilot is much more than a fun tool, or even excellent auto-complete. Rather, I will argue that Copilot fundamentally changes programming.

This is a bold statement. [The history of technology is littered with people being wrong about bold statements](https://www.telegraph.co.uk/technology/0/worst-tech-predictions-of-all-time/thomas-watson-ibm-president-in-1943/). My reasons for nevertheless writing this post is a) I think the general attitude in the data science community is slightly too bearish, and I hope this article can help shift the tides even by a bit, b) I would love to change my mind on this, and c) I’m genuinely awestruck.

## Why be impressed?

To understand my awe, we first need to discuss how hard a problem code-generation is compared to other problems in machine learning. (SPOILER: it is really hard). Take the “simple” example of [predicting house prices](https://www.kaggle.com/c/house-prices-advanced-regression-techniques). When you start training a classifier it will perform poorly: It might predict a price of $100,000 when the real price is $200,000. However, it is really easy to a) say exactly how wrong the prediction is (-$100k) and b) tell the model how to improve (i.e. adjust these weights using some optimization algorithm).

This is NOT the case for code generation. It is a long-standing meme among programmers that even a [single misplaced semi-colon can wreck havoc on your code](https://vincentdnl.com/programming-memes/). Adjusting the output slightly will not produce slightly different results; it will most likely produce a syntax error. And even if the program runs, it will very probably have a radically different output.

Even natural language, which has [a notorious reputation in AI for being complex](https://theinfinitekitchen.com/faq/faq-why-natural-language-understanding-is-difficult/), is more forgiving. Even if you’re text is filed with spelling mitsakes adn rong words, most people still understand the meaning.

And yet, OpenAI solved it. Even for relatively complex prompts like “[train a logistic regression on MNIST data and output the confusion matrix](https://dmkothari.github.io/Machine-Learning-Projects/Logistic_Regression_with_MNIST.html)”, the output is decent. Sure, it might not fit one’s personal style and might assume a funky folder-structure but it is *sensible*.

## Where Copilot fails

You might now be thinking “It’s neat that it can do logistic regression, but it failed miserably when doing X”, where X stands for whatever data science problem you were working on. From my own (limited) experience with Copilot I have experienced several X’s including:

1. Scraping data from arbitrary websites
1. Domain specific data transformations (i.e. extracting mentions of [public benefit](https://en.wikipedia.org/wiki/Benefit_corporation) AI companies in news articles)
1. Long complex specifications (i.e. copy-pasting your homework description into a python file (don’t judge!))

While all of these are tasks regularly encountered by data scientists, it is important to understand the magnitude of what is required to solve them. Scraping data from arbitrary websites would basically require Copilot to have an accurate view of the structure of every single website (AND understand what output is required). Understanding niche domain specific transformation would imply that Copilot “understands” every single domain data scientists work within (which is becoming [most domains](https://www.analyticsinsight.net/data-is-here-data-is-there-data-is-everywhere/)!). And understanding long-complex specifications would basically mean completely automating the job of data scientist (and making my homework a lot easier).

What all of these problems have in common is that they are in some sense [*A(G)I-complete*](https://en.wikipedia.org/wiki/AI-complete), which means that having an AI solve them would require general intelligence. This would imply that there is a long way to Copilot) revolutionizing anything. Especially since [AGI has been just around the corner for a long time](https://www.openphilanthropy.org/focus/global-catastrophic-risks/potential-risks-advanced-artificial-intelligence/what-should-we-learn-past-ai-forecasts).

Or would it? Copilot doesn’t need to solve *all* of our problems to be a game changer. Even it solves ~20 percent it would save a lot of time.

It is important to remember that Copilot went from the impossible to something that kind of works; they went from [zero to one](https://en.wikipedia.org/wiki/Zero_to_One). Taking that first leap is often the difficult part. It took approximately ~12,000 years for humans to learn how to fly. It took merely 60 more to get to the moon. And if [current scaling laws hold](https://arxiv.org/abs/2001.08361), Copilot might go quite a bit faster.

## Copilot changes the way you code

Now that I have laid out the big-picture reasons for *why* I believe Copilot is a game changer it’s time to get into the *how* it changes the game. A good place to start is that Copilot changes the way you code.

When I started playing around I quickly realized that I was very quick to adapt my coding style. Before Copilot (B.C.) my coding experience was a rapid iteration of getting an idea, trying to make it work, googling the problem, and implementing stack overflow / some blog post / some paper. This approach has served me (and many of my programmer friends) well.

![The typical developer workflow](/images/copilot-workflow-before.png)
*The typical developer workflow (at least for me). Each different color is a context switch.*

After Copilot (A.C.) the flow looks different. In my experience, I spend more time thinking about *how* I want the program to work, then how to specify that through a comment / function header, and then evaluating the outcome — also in an iterated fashion.

![The (idealized) workflow with Copilot](/images/copilot-workflow-after.png)
*The (idealized) workflow with Copilot. You come up with an idea and then review the code produced by copilot. Notice the lack of context switching.*

The shift is simple yet profound. While the experience is markedly different there are three main themes:

1. **Copilot makes you an architect:** Because Copilot turns comments into code, you can spend more time and energy thinking about the overall structure of the code. In that sense your role becomes more akin to a software architect than a programmer.
1. **Copilot makes it easier to try new frameworks:** Simply writing “scrape randomsite.com for stuff using [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)” makes Copilot give you output that is fairly well structured. This makes it much easier to modify the code for the specifics of your project.
1. **Copilot reduces context switches:** This is a major one. Often Copilot replaces [Stack Overflow](https://stackoverflow.com/) as the first source of help. This makes you do much more inside your IDE without getting distracted by the wonders of the internet.

In the above I do exaggerate a bit. I still spend much time on stack overflow and “manually” working out the kinks where Copilot (inevitably) fails. The reason for my exaggeration is to open up your eyes for how this could work. As one of my favorite YouTubers, [Two Minute Papers](https://www.youtube.com/channel/UCbfYPyITQ-7l4upoX8nvctg), is fond of saying: “two more papers down the line and who knows where we’ll be”. What a time to be alive!

## On data jobs (and the potential lack thereof)

Now maybe some of my fellow data scientists have been reading this and started to look for courses in hairdressing, therapy, executive decision making, or other [hard to automate tasks](https://www.sciencedirect.com/science/article/abs/pii/S0040162516302244). After all, haven’t I just argued that Copilot will steal our jobs?

Not quite. My main argument is that Copilot *changes* the game not that it removes it. The relationship between jobs and technology is complicated. However, one fairly robust finding is that sophisticated technology makes highly skilled workers *more valuable*. Copilot might therefore *increase* the demand for data scientists by a) opening the job up to domain experts and b) increasing the productivity of data scientists.

The key reason is that AI systems (like Copilot) [automates *tasks* not *jobs*](https://www.forbes.com/sites/joemckendrick/2018/08/14/artificial-intelligence-will-replace-tasks-not-jobs/). No matter how much it often feels like it, the job of a data scientist is much more than writing boilerplate and cleaning data. The most high-value skills are more unstructured like creating and delivering business-critical metrics, communicating with stakeholders, and other business stuff.

It is not all great news for data scientists. By [automating the boring stuff](https://automatetheboringstuff.com/), Copilot favors experienced data scientists, who have a strong knowledge of [software design principles](https://betterprogramming.pub/10-design-principles-in-software-engineering-f88647cf5a07) and how to structure projects. But what about junior data scientists (and other programmers) who still have to learn how to write [SOLID code](https://www.geeksforgeeks.org/solid-principle-in-programming-understand-with-real-life-examples/) and other essential patterns? How are they supposed to distinguish between good and bad suggestions?

There’s probably no easy answers to these questions. But I hope through this article that the questions will at least be discussed. While I have been phrasing this article rather strongly, I’m more than happy to change my mind if there are key arguments I have missed. Until then I will enjoy my new wingman — right until I’m replaced (hopefully not by a [paperclip](https://www.lesswrong.com/tag/paperclip-maximizer)!).

## Acknowledgements

This article is based on conversations with Andrei Alexandru, [Esben Kran](https://kran.ai/), and Luke Ring. Especially thanks to Esben for reading the rough first draft. All views and errors are my own.
