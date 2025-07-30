import pywebio

class Bubble:
    def __init__(self, color="#cccccc", textSize:str="small", position:str="left"):
        self.color = color
        self.textSize = textSize
        self.margin = "left" if position == "right" else "right" ## invert position to margin
        self.css = f"background-color:{self.color}; border-radius:2em 2em; padding:1em; font-size:{self.textSize}; margin-{self.margin}:2em;"

    def output(self, markdown:str) -> None:
        """render a string into a text-bubble
        """
        pywebio.output.style(
            pywebio.output.put_markdown(markdown),
            css_style=self.css
        )

    def input(self) -> str:
        query = pywebio.input.textarea("ask anything...",)
        self.output(query)
        return query

    def loading(self) -> pywebio.output.Output:
        return pywebio.output.style(
            pywebio.output.put_loading(),
            css_style=self.css
        )

if __name__ == "__main__":
    import time

    user = Bubble(color="#aaeeaa",position="left")
    agent = Bubble(color="#bbbbbb",position="right")
    agent.output("hello, you may ask!")
    while True:
        query = user.input()
        with agent.loading():
            time.sleep(2)
        agent.output("anser")