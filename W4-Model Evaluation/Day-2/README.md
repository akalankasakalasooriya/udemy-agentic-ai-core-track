# Reading Leaderboards and Commercial Use: Important Notes

`1-leaderboard.ipynb` runs four quick questions against the Azure deployments and ranks them by correct answers, then by estimated cost. It is a teaching example, not a real leaderboard.

## The five leaderboards

- **Artificial Analysis**: a broad intelligence index. It also shows price and speed, so it is the best place to compare intelligence with cost.
- **Vellum**: includes API cost and context window. Useful when you need to fit a model into a product budget.
- **Scale.com SEAL**: private evaluations written so that models have not seen the questions. Harder to game.
- **Hugging Face open-source leaderboards**: open-weight models only. The old Open LLM Leaderboard has been archived, so check the current Hugging Face leaderboard spaces before you cite a number.
- **LiveBench**: contamination-free. Questions refresh over time, so leaked answers go stale.

## LM Arena and Elo

- LM Arena shows two anonymous answers to the same prompt. People vote for the better one.
- Votes produce Elo-style ratings, the same idea used in chess.
- Good for general preference. Weak on accuracy for hard tasks, and it reflects how people vote, not whether the answer is correct.

## Cost against intelligence

- Compare models on the same task, not on a general score.
- A model that is slightly less capable but much cheaper can win a high-volume job.
- Check the price per million input and output tokens on your Azure resource. The prices in the notebook are examples only.

## Commercial use cases

- **Automation**: the model does a repeatable task, and a person checks exceptions. Measure error rate on real cases before you switch it on.
- **Augmentation**: the model drafts, and a person edits and decides. Measure time saved and quality, not only accuracy.
- **Agentic AI**: the model picks tools and takes several steps. Add limits, logging, and a stop rule. Errors compound across steps.

## Notes for our course

- Do not treat one leaderboard as the answer. Use two or three sources, then test on your own task.
- Leaderboards change often. Record the date and the model version when you compare results.
