import os
import httpx
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Log, Button, Label, TextArea, Static
from message_builder.builder import IataMessageBuilder
from textual import work
from google.cloud import pubsub_v1

os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8085"
PROJECT_ID = "iata-teletype-project"
TOPIC_ID = "teletype-messages"
SUB_ID = "teletype-sub"

API_URL = "http://localhost:8000/messages/teletype"

class TeletypeApp(App):
    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-view"):
            yield Log(id="output-log")
            with Vertical(id="config-window"):
                yield Label("Destination Config", id="config-title")
                yield Static("Enter 7 chars...", id="config-content")
        
        with Container(id="input-form"):
            yield Label("Teletype Sender (Enter file:path.txt in Body to load from file)", id="form-label")
            with Horizontal(id="top-row"):
                yield Input(placeholder="Dest", id="in-dest", classes="in-small")
                yield Input(placeholder="Orig", id="in-orig", classes="in-small")
                yield Input(placeholder="Tag", id="in-tag", classes="in-small")
                yield Input(placeholder="Order", id="in-ord", classes="in-small")
                yield Button("Send", id="btn-send", variant="primary")
            yield TextArea(text="", id="in-body", show_line_numbers=False)
        yield Footer()

    async def on_mount(self):
        self.log_widget = self.query_one("#output-log", Log)
        self.setup_subscription()
        self.start_listening()

    def setup_subscription(self):
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
        # Create topic first because subscriber creates fail if topic not exists
        try:
            publisher.create_topic(request={"name": topic_path})
        except Exception:
            pass

        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(PROJECT_ID, SUB_ID)
        
        try:
            subscriber.create_subscription(request={
                "name": subscription_path, 
                "topic": topic_path,
                "enable_message_ordering": True
            })
            self.log_widget.write_line(f"[System] Subscribed using ordering keys on {SUB_ID}.")
        except Exception as e:
            pass

    @work(exclusive=True, thread=True)
    def start_listening(self):
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(PROJECT_ID, SUB_ID)

        def callback(message):
            raw_data = message.data.decode("utf-8", errors="replace")
            # Enhance readability for control characters without markup
            safe_data = (
                raw_data.replace('\x01', '<SOH>')
                .replace('\x02', '<STX>')
                .replace('\x03', '<ETX>')
                .replace('\x04', '<EOT>')
                .replace('\r', '<CR>')
                .replace('\n', '<LF>\n')
            )
            ord_key = message.ordering_key if message.ordering_key else "None"
            
            self.call_from_thread(
                self.log_widget.write_line, 
                f"==== New Message: Order Key: {ord_key} ====\n{safe_data}\n"
            )
            message.ack()

        try:
            # We must use threading / block for subscriber to continuously poll in textual's worker
            self.log_widget.write_line("[System] Listening for PubSub messages...")
            future = subscriber.subscribe(subscription_path, callback=callback)
            future.result()
        except Exception as e:
            self.call_from_thread(self.log_widget.write_line, f"[Error] PubSub listen error: {e}")

    @work(exclusive=True, thread=False)
    async def call_api(self, payload: dict):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(API_URL, json=payload)
                self.log_widget.write_line(f"[Client] Payload sent. Server replied: {response.json()}")
            except Exception as e:
                self.log_widget.write_line(f"[Client Error] Failed calling API: {e.__class__.__name__} - {str(e)}")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-send":
            dest = self.query_one("#in-dest", Input).value.strip()
            orig = self.query_one("#in-orig", Input).value.strip()
            tag = self.query_one("#in-tag", Input).value.strip()
            ord_key = self.query_one("#in-ord", Input).value.strip()
            body_input = self.query_one("#in-body", TextArea).text.strip()

            if not dest or not orig or not body_input:
                self.log_widget.write_line("[Error] Destination, Origin, and Body are required.")
                return

            if body_input.startswith("file:"):
                filepath = body_input.replace("file:", "")
                if os.path.exists(filepath):
                    with open(filepath, "r") as f:
                        body_content = f.read()
                else:
                    self.log_widget.write_line(f"[Error] File not found: {filepath}")
                    return
            else:
                body_content = body_input

            payload = {
                "destination": dest,
                "origin": orig,
                "body": body_content
            }
            if tag: payload["tag"] = tag
            if ord_key: payload["ordering_key"] = ord_key

            self.call_api(payload)

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "in-dest":
            val = event.value.strip()
            if len(val) >= 7:
                rule = IataMessageBuilder.get_rule(val)
                content = (
                    f"Suffix: \[ {rule['suffix']} ]\n"
                    f"CCITT5: {'[yellow]TRUE[/]' if rule['ccitt5'] else '[green]FALSE[/]'}\n"
                    f"EOT:    {'[red]ENABLED[/]' if rule['eot_enabled'] else '[green]DISABLED[/]'}"
                )
                self.query_one("#config-content", Static).update(content)
            else:
                self.query_one("#config-content", Static).update("Enter 7 chars...")

def run():
    app = TeletypeApp()
    app.run()

if __name__ == "__main__":
    run()
