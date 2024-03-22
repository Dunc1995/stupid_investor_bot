import argh
import stupidinvestorbot.app as app

if __name__ == "__main__":
    argh.dispatch_commands([app.get_coin_summaries, app.monitor_coin])
