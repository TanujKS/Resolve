# Resolve
A webapp for summarizing Congressional bills using GPT-3 to allow all citizens to understand how issues are being dealt with in Congress. Submitted to CAC 2022 (CA-18)


# Our Mission
Too many citizens here in the United States are discouraged from participating in politics with all the political jargon and legal language. Resolve aims to solve that problem by using advanced Artificial Intelligence and Machine Learning to explain Congressional bills in language humans can understand.


# Congressional Bills
Bills are a proposal put before a body of Congress. Bills are written by a Representative, then handed over a committee of experts on the topic. It is then voted on with a simple majority and passed to the other branch of Congress which then repeats the process. After passing both the House and the Senate it is put on the President's desk where they can either veto it or pass it as law. Bills are denoted by the House they originated in, such as HR for House Resolutions and S for Senate Resolutions

## Joint Resolutions
Joint resolutions are very similar to bills, but are generally used for specific matters or amendments to the Constitution, where they do not require the signature of the President if they have a 2/3s vote from both Houses. Joint Resolutions are denoted by the house they originated in followed by JRES (Joint RESolution)

## Concurrent Resolutions
Concurrent resolutions require approval from both Houses but do not require the Signature of the President as they do not have the effect of the law. They are mainly used to convey the sentiment, views, or beliefs of Congress as a whole. Concurrent resolutions are denoted by the house they originated in followed by CONRES (CONcurrent RESolution)


## Simple Resolutions
Simple resolutions is a proposal only pertaining to one branch of Congress. It does not require the approval of the other House or the President as it does not have the force of law. They are generally used to express the sentiment, views, or beliefs of a single House. Simple resolutions are denoted as the House they pertain too followed by RES (RESolution)

# How It Works

## Summaries
Resolve uses OpenAI's GPT-3 models through their API to provide well-written summaries and briefs about complex bills.

## Relevancy
To show users bills that are pertinent to current events, Resolve pulls thousands of posts from the popular subreddit r/Politics daily and gives all the Congressional bills stored in a database a 'relevancy score' using a cosine simliarity model, which then allows the bills to be ranked from most relevant to least.

## Search Engine
To help users find bills that matter to them, Resolve uses cosine similarity to compare a queries sentiment, not just words, to a database of all Congressional bills.    
