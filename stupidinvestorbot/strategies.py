from stupidinvestorbot.models.app import CoinSummary

STRATEGY_CONSERVATIVE = "Conservative"
STRATEGY_HIGH_GAIN = "High_Gain"


class CoinSelection:

    @staticmethod
    def conservative(summary: CoinSummary) -> bool:
        """Selects a coin that has near 0% change in the last 24 hours,
        but with high volatility (standard deviation).

        Args:
            summary (CoinSummary): Coin data to analyse.

        Returns:
            bool: True if the coin is volatile but with 0% change in the most recent trade.
        """
        return (
            summary.has_high_std and summary.has_low_change and summary.is_large_volume
        )

    @staticmethod
    def high_gain(summary: CoinSummary) -> bool:
        """Selects a coin that is within its standard 24h deviation but
        experiences high gain.

        Args:
            summary (CoinSummary): Coin data to analyse.

        Returns:
            bool: True if the coin is within standard deviation.
        """
        mean = float(summary.mean_24h)
        std = float(summary.std_24h)
        return (
            bool(float(summary.latest_trade) - (mean + std) <= 0)
            and summary.percentage_std_24h > 0.03
            and summary.is_large_volume
        )

    @staticmethod
    def should_select_coin(summary: CoinSummary, strategy: str):
        select_coin = False

        match strategy:
            case "high_gain":
                select_coin = CoinSelection.high_gain(summary)
            case "conservative":
                select_coin = CoinSelection.conservative(summary)
            case _:
                select_coin = False

        return select_coin
