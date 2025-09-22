from langchain.prompts import PromptTemplate


class PromptBase:
    prompt = 'you are a helpful assistant.'
    output = ''

    def format(self, **kwargs):
        prompt_template = PromptTemplate.from_template(self.prompt)
        if not self.output:
            self.output = ''
        return prompt_template.format(**kwargs) + self.output

    def entity(self):
        return self.prompt + self.output
