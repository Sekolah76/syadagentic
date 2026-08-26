# Gemini Markdown Sanitization

When switching auto-reply content generation from Claude (which strictly follows "no formatting" system prompts) to Gemini (e.g., `ag/gemini-3-flash-agent`), Gemini often leaks conversational markdown artifacts into the output, such as `**Start:**`, `**Agreement:**`, or bullet points, breaking the natural Gen-Z illusion.

Always apply a regex sanitizer before posting Gemini-generated social content:

```python
# Strip LLM conversational preambles and bold markdown
text = re.sub(r'^\s*(Start|Agreement|\*\*|\*).*?:\s*', '', text)
text = text.replace('\n', ' ')
text = re.sub(r' +', ' ', text)

# Sanity: remove quotes if LLM wrapped reply
text = text.strip('"\'')
```