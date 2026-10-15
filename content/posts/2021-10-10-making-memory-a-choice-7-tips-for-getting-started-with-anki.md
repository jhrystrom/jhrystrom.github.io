---
title: "Making Memory a Choice: 7 Tips for Getting Started with Anki"
date: 2021-10-10
---

<aside class="note" markdown="1">
This article was originally published on [Medium](https://medium.com/@jhvithamar/making-memory-a-choice-7-tips-for-getting-started-with-anki-4fd138aee3a8). It has been ported to my own site with Claude Code
</aside>

![Photo by Fredy Jacob on Unsplash](/images/making-memory-a-choice-7-tips-for-gettin-1.jpg)
*Photo by [Fredy Jacob](https://unsplash.com/@thefredyjacob?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

We forget most of what we read. That is a fact of human cognition just like we get [fooled by visual illusions](https://michaelbach.de/ot/) and have a hard time [thinking intuitively about statistics](https://en.wikipedia.org/wiki/Intuitive_statistics). But wouldn’t it be nice if we had a tool to help us remember? A tool that could [make memory a choice](https://notes.andymatuschak.org/Spaced_repetition_memory_systems_make_memory_a_choice)?

Incredibly, such a tool exists. The fundamental technique is called [spaced repetition](https://elitemedicalprep.com/what-is-spaced-repetition-and-why-is-it-so-important/). The fundamental idea is to write some flash cards (or prompts), where you increase the time between reviews for each time you answer it correctly (see figure 1). If you misremember a prompt it goes all the way back to the beginning.

![Example of spaced repetition borrowed from Gatterbauer and Sucio, 2011](/images/making-memory-a-choice-7-tips-for-gettin-2.png)
*Example of spaced repetition borrowed from [Gatterbauer and Sucio, 2011](https://www.researchgate.net/publication/220988194_Managing_Structured_Collections_of_Community_Data)*

Luckily, we don’t need to keep track of physical boxes to reap the benefits of this awesome technique. There are some great apps out there that manages all the tedious stuff for you. The most popular of these is [Anki](https://apps.ankiweb.net/).

Anki is free, open source and has a great community. It works by you writing prompts which are basically flash cards with a question and an answer (with a few more advanced options). You can then organize your prompts into decks. These decks can then be shared to Anki’s website where you can also download other people’s decks.

I have been using Anki for a little less than a year and it has transformed the way I learn. However, it can be daunting to take the first steps on your spaced repetition journey. This is why I have compiled these seven tips to help you get started.

(It should be noted that I have absolutely no affiliation with Anki other than being very happy with the software)

## 1. Write you own cards

Anki has a great community who provides [hundreds of decks](https://ankiweb.net/shared/decks/) for free online. When you’re starting out it can seem like an easy path to Anki-greatness as you can easily amass hundreds of cards. This is surely much easier than actually doing the hard work of writing the cards yourself?

However, downloading decks is like taking an elevator to the top of Mount Everest: You’ll get there but you won’t be acclimatized and will probably asphyxiate. Okay, that last bit is probably over the top (no pun intended), but the acclimatization metaphor checks out. Everyone has a slightly (and sometimes vastly) different way of understanding concepts. This can make it frustrating to adapt other people’s cards as many of them either seem irrelevant or weirdly phrased.

Writing your own prompts solves the problem. It makes the cards relevant to *you.* You can phrase the prompts in a way that you understand. You can also focus on writing prompts about the concepts that matter to you. This has the added benefit of making you engage more with the texts you read which has shown to be much [more effective for understanding](https://www.readingrockets.org/booklists/cognitive-science-reading).

## 2. One deck to rule them all

Most people are used to organize their notes in neat folders for e.g. subjects in school. Intuitively, it might make sense to use the same method for organizing Anki-decks; one deck per subject. I would argue to do the complete opposite: One deck is all it takes.

There are two reasons for only having one deck. The first is reducing friction. Having one deck means that you don’t have to actively decide which deck a prompt is most suited for. This is especially relevant if you are writing prompts about things outside of a school context (which you definitely should!). It is also easier to only review one deck, which makes it more likely you will stick to it.

The second reason is that it inspires you to see connections across subjects. If a prompt about automatic machine learning is followed by a prompt about explainable AI, you might be inspired to [write about it](/posts/2021/07/can-explainable-ai-be-automated/) (\*hint\*, \*hint\*). The world doesn’t separate into neat, distinct boxes and neither should your knowledge of it. Noticing connections between different subjects can give you some great ideas and having one deck helps you achieve just that!

## 3. Sync Desktop and Mobile

Anki can be used both on desktop and on mobile (at least if you have an Android). Both platforms have different strengths. Desktop is faster for writing prompts (especially if you learn a few shortcuts!) and makes writing prompts while studying more seamless (especially if you’re used to reading and writing on your computer).

Mobile is, well, mobile. This makes it easier to write prompts when you are reading a book or listening to a podcast. It also makes it easier to review if you have some time to kill with your phone in hand (which probably happens fairly often).

Luckily, we can get the best of both worlds by syncing them. This can be done relatively easily using AnkiConnect.

## 4. Break Concepts down into Multiple Prompts

Now that we have covered a good set-up for Anki, it is time to discuss how to write good prompts. One good practice is to break down new concepts into multiple prompts.

Say, for example you just learned about the Pythagorean Theorem. You might encapsulate your new knowledge in the prompt: “What is the Pythagorean Theorem?”. Are you talking about mathematical equation (“a²+b²=c²”)? Or maybe the geometrical interpretation (“the relation between the length of the hypotenuse and the sides”)? Or even the social context (“the first geometric theorem taught to middle schoolers”).

The problem with this is that the answer is ambiguous and unfocused. You might come up with different answers each time you encounter the question which won’t strengthen your memory as much.

A better approach would be to use what Andy Matuschak calls [*atomic prompts*](https://notes.andymatuschak.org/z8kPjeqPqJwLwqdVqPYBBTwfU3aczsFyvXFmx). That means breaking down the concept into small chunks with one clear and correct answer. For the previous question this could be the following questions: *What geometric relationship does the Pythagorean Theorem describe? and What is the equation of the Pythagorean Theorem?* I think those two questions capture the essence of the Pythagorean Theorem but some people might want to write more prompts.

One perceived drawback of writing many prompts is the additional time it adds to your reviewing. However, this adds less time than one might. Due to exponential scheduling, a well-written Anki prompt will only take a few tens of seconds for it to be memorized forever! An unfocused prompt that you struggle to memorize will take much longer. Therefore it might even *save you time* to write more but simpler cards

## 5. Use Cloze deletions for exactitude

Making atomic prompts will get you much of the way to more specific and focused prompts. But what if you need to remember something word for word? This is were cloze-deletion shine.

Cloze deletions are Anki-terminology for “guess the blank word”. An example could be “to be or not to be, that is the \_\_\_\_\_” (Where the answer is “question”). Cloze deletions work well, when you need to remember something exact. This could be quotes (like the one above), lists or mathematical formulas.

I have personally used cloze deletion to remember Shakespeare’s 18th sonnet (“Shall I compare thee to a Summer’s day?”), the equation for pointwise mutual information, and a beautiful quote about math (“math is the distilled heart of thinking”). It is important when writing cloze deletions to cloze the meaning-bearing words / sentences and not the fillers. There is not much sense in having a card that says “To be or not \_\_ be; that is the question”

## 6. Make Anki a habit

Now that we have covered both advice for setting up and concrete writing advice it is time to zoom out and talk about process. The most important factor determining whether you will have success with Anki (and Spaced Repetition in general) is whether you successfully make it a habit.

As [James Clear](https://jamesclear.com/) describes in his magnificent book *Atomic Habits*, habits are ways to make small changes have tremendous effects. This is especially true with Anki. Imagine that you consume ten pieces of content per day (like book chapters, educational YouTube-videos, or a blog posts). For each you write three small, atomic prompts. This would translate into almost 11,000 new pieces of knowledge that you otherwise might have forgotten!

The reviewing process also becomes much easier the more consistent you are. Continuing with the above example, you will still spend maybe 5–10 minutes a day reviewing. For most people this will be a neglectable fraction of the time they spend doing other stuff on their phone.

Putting it together, you can learn 11,000 new things per year for an investment of 15–20 minutes a day. That is a gigantic return of investment. Even if you only write 10 prompts a day (as I have probably averaged) it is still a huge gain in knowledge compared to what you otherwise would have remembered.

## 7. Learn from the Pros

“[Prompt writing is a skill](https://notes.andymatuschak.org/Writing_good_spaced_repetition_memory_prompts_is_hard)” as Andy Matuschak once put it. And as with many other skills it is vastly easier to stand on the shoulders of giants than to learn everything from scratch. Ernő Rubik, the inventor of the Rubik’s cube, [spend over a month solving it for the first time](https://www.nytimes.com/2020/09/16/books/erno-rubik-rubiks-cube-inventor-cubed.html#:~:text=The%20first%20person%20to%20solve,architecture%20professor%20named%20Erno%20Rubik.). Today, after decades of incremental improvement, the world record is [3.47 seconds](https://www.worldcubeassociation.org/results/records)! This is only possible because aspiring speed cubers could learn from the hard-won experience of former champions.

I too have learned much from the champions of spaced repetition. Matuschak, whom I have mentioned a few times throughout this post, has been especially influential. Many of the ideas including creating atomic prompts and the importance of writing your own prompts stems directly from his thinking. One article that I cannot recommend enough is his masterpiece [“How to write good prompts: using spaced repetition to create understanding”](https://andymatuschak.org/prompts/).

I can also recommend browsing through his [personal note-collection](https://notes.andymatuschak.org/Spaced_repetition_memory_systems_make_memory_a_choice), where he shares his insights on spaced repetition and how to improve your thinking more generally. It is definitely among one of the most inspiring online rabbit holes I’ve ever fallen into!

There are of course also many other Anki-experts out there who have shared their experiences, so do go out and explore this awesome craft.

Thanks for reading and good luck with your Anki Journey!
