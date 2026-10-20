---
title: "The Claude Code Sovereignty Paradox"
date: 2026-10-20
---

![Servers in a Landscape by Deborah Lupton](/images/servers-in-a-landscape.png)
*[Deborah Lupton](https://betterimagesofai.org/whoWeAre) / [Servers in a Landscape](https://betterimagesofai.org/images?artist=DeborahLupton&title=ServersinaLandscape) / [Licensed by CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)*

Once upon a (not so distant) time, I started two writing projects: my BSc thesis and my Medium blog. Actually, it was really only one project; my wonderful BSc supervisor had taught me that writing early in research is a great way to distil thoughts and make tangible progress. Great advice that I still try to follow (thanks, Rebekah!). Throughout the following months (and years), I wrote about [whether Explainable AI can be automated](/posts/2021/07/can-explainable-ai-be-automated/) (no), whether we can be sure [that AGI is impossible](/posts/2021/08/certainty-is-expensive-a-campfire-chat-about-agi-and-overconfidence/) (also no), whether [XAI is helpful or harmful](/posts/2021/09/is-explainable-ai-helpful-or-harmful/) (it depends), and many other things from [surveillance capitalism](/posts/2022/01/surveillance-capitalism-a-data-scientists-perspective/) to [Anki](/posts/2021/10/making-memory-a-choice-7-tips-for-getting-started-with-anki/) and (my personal favourite) [how GitHub Copilot was a game changer in 2022](/posts/2022/04/github-copilot-is-a-game-changer/).

A curious reader might have noticed that the links above send you to my personal website -- not Medium. Recently, I migrated all of my blog posts from Medium to this page. There are [many reasons to dislike Medium](https://dev.to/taillogs/why-medium-actually-sucks-203): their economics are platform-like, the UX is bad, authors lack control, etc. Up until recently, these dislikes were outweighed by the bother of (1) setting up my own website and (2) migrating all the blog posts. However, both problems have now disappeared thanks to coding agents, specifically Claude Code.

## Migration: from complex to prompt

Migrating platforms used to be daunting and tedious. I would've had to go to each Medium article manually (Medium doesn't have a great API); copy the text; download the images; format them into Markdown; and integrate them with my personal website. Boring manual work that I'd rather not do -- and therefore didn't.

Now, all of that boring work was a single prompt to Claude Code:

```
https://medium.com/@jhvithamar ---
Please add all my medium articles to the blog.
No need to add extra comments, just a simple box at the top that says:
"This article was originally published on [Medium](link to original).
It has been ported to my own site with Claude Code"
```

I sent off the prompt with a `caffeinate` command (while I went to caffeinate myself), and five minutes later, all of the blog posts were nicely formatted. Super easy, barely an inconvenience.

## The sovereignty paradox

As mentioned, I wanted to escape Medium to take back control of my blog. To do so, I relied on another Big Tech product, namely Claude Code. On the face of it, this seems like a paradox: haven't I just replaced one platform (Medium) with another (Claude Code)?

This paradox goes beyond my personal blog. Many organisations are currently stuck with legacy platforms, which coding agents -- especially frontier coding agents -- could help them escape. However, these organisations (and I) might wonder whether this will really give them meaningful control.

A brief resolution to the paradox is to think about the _outputs_ of the process. While I used Claude Code to do the migration, the results are just a collection of Markdown files in a Git repository. If Anthropic closed my account tomorrow (or restricted access to their newest models), I would still have my Markdown files.

Of course, the Markdown file you're currently reading is still on a Big Tech platform, namely GitHub. However, the _code_ to build the page is mostly Python. If GitHub closed down tomorrow, I could still migrate to another platform.

## Conclusion: use coding agents to build controllable tech

My main lesson can be put concisely: coding agents are great for making your technology more sovereign. Even if the agents disappear, the technology you've built remains.
