---
title: 'Research projects are IT projects - and IT projects are delayed'
date: 2025-01-07
permalink: /posts/2025/01/research-it-project/
tags:
  - cool posts
  - meta
---
![Artist rendition of changing code late in a research project](/images/distressed-researcher.webp)
*Artist rendition of changing code late in a research project*

We've all been there: What starts as a small research idea grows into a paper draft, and suddenly you need to add new conditions, try different models, or analyze the data in a new way. Before you know it, your codebase has turned into spaghetti, and making changes becomes a dreaded task. What began as an exciting research question becomes bogged down in technical debt caused by hacky choices made by a slightly younger but much more foolish version of yourself. If only there were a way to avoid this madness.

## Research Projects Are IT Projects
Every computational research project involves a pipeline of code: creating experiments, transforming data, running analyses, and communicating results through plots and tables. While not every project will need changes in all these areas, the possibility for change is always there. A reviewer might request additional analyses, a new model might be [released during write-up](https://openai.com/index/gpt-4-research/), or you might need to rerun the experiments on a new laptop due to a coffee-related accident (all, unfortunately, inspired by true events).

Many researchers might argue that code quality isn't a significant concern for bespoke analyses. After all, if you're just running an experiment once, why spend time on software design? This perspective breaks down as soon as changes are needed - and in research, changes are almost inevitable. Whether it's exploring different conditions, incorporating new data, or responding to reviewer feedback, the ability to modify your analysis pipeline becomes crucial.

## IT Projects Are Notoriously Late
Bent Flyvbjerg's [iron law of (mega)project management](https://academic.oup.com/edited-volume/28080/chapter-abstract/212102359?redirectedFrom=fulltext) states that projects run over time, over budget, over and over again. 

While IT seems less 'mega' than building an opera house, [IT projects are especially susceptible to overruns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4204819) - and research code is no exception. The statistics are stark: IT projects consistently show significant cost and time overruns, with many failing to deliver their intended benefits.

The warning signs of troubled research code are familiar to many: Setting up your project on a new machine becomes a multi-hour ordeal, onboarding collaborators requires lengthy documentation of manual steps, and making changes to your analysis pipeline feels like walking through a minefield. Each modification requires careful navigation through layers of interdependencies, and what should be simple changes balloon into major refactoring efforts.

For researchers, this translates directly into lost opportunities. Time that could be spent exploring novel ideas is instead consumed by debugging and deciphering old code. Hours disappear into setting up environments, tracking down dependencies, and trying to remember the exact sequence of manual steps needed to reproduce results.


## The Solution: Software Design (but not too much)
Fortunately, there are ways to combat the iron law. Here's a good heuristic: Your research ideas should be advanced and novel - your code should be as simple (and modular) as possible. This isn't a call to implement every design pattern under the sun or to create elaborate architectures. Instead, it's about making your code easy to change and your analyses reproducible.

The software development community has spent decades learning how to manage complexity and change. [The Pragmatic Programmer](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/), [the Phoenix Project](https://www.amazon.com/Phoenix-Project-DevOps-Helping-Business/dp/0988262592), and other resources offer valuable lessons that researchers can adapt. The goal isn't to turn researchers into software engineers, but to borrow proven practices that make code more maintainable.

A concrete example: In projects for [evaluating political bias in embedding models](https://github.com/jhrystrom/wicked-fair), I benefited greatly from creating a simple interface that treats embedding models as functions that turn text into vectors. Adding a new model merely requires adapting it to this interface, and it slides right into the existing analysis pipeline. This modular approach, widely recognized both in project management and software engineering, helps manage complexity and makes changes easier.

While writing well-designed software is a (fun) journey that takes years (except if/when generative models take over), here are a two good places to start:
1. Have a fully automatic way of reproducing environments across machines (I use [uv](https://docs.astral.sh/uv/)). This eliminates the "it works on my machine" problem and makes your research immediately accessible to collaborators and reviewers.
2. Design for change from the start - make going from one to two cases as easy as going from two to n. This often means taking a moment to think about abstraction when you create an addition. Ask yourself: "How can I make it simple to add yet another condition/model/metric here?"

These practices not only save time but also make your research more reproducible and cumulative. After all, science advances faster when we can build on each other's work effectively. Good software design isn't just about clean code - it's about enabling the iteration and collaboration that drives scientific progress.
The next time you start a research project, take a moment to think about how it might evolve. A small investment in software design upfront can save hours of frustration later and let you focus on what really matters: the research itself.
