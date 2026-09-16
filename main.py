import httpx


class ExchangeError(Exception):
    "Base class for all exchange-rate lookup related errors"


class NetworkError(ExchangeError):
    "API call network failed"


class UserInputError(ExchangeError):
    "Error from the user input"


class InvalidBaseCurrencyError(UserInputError):
    "The base currency passed to the API was invalid"


class InvalidTargetCurrencyError(UserInputError):
    "The target currency passed to the API was invalid"


class InvalidAmountError(UserInputError):
    "The amount inputted was inavlid"


class UnexpectedResponseError(ExchangeError):
    "Every other non-success status, can't understand the result we got"


def ConvertCurrency(Amount: int, ExchangeRate: float) -> float:
    Converted = Amount * ExchangeRate
    return Converted


def FetchExchangeRate(Base: str, Target: str) -> float:
    """
    Fetches the exchange rate float from two currencies
    Possible Errors:
        NetworkError,
        InvalidTargetCurrencyError,
        UnexpectedResponseError
    """

    try:
        response = httpx.get(
            "https://api.frankfurter.dev/v1/latest", params={"base": Base}
        )
    except httpx.RequestError as exc:
        raise NetworkError(f"Could not fetch frankfurter: {exc}") from exc
    else:
        if response.status_code == 200:
            try:
                Data = response.json()
                try:
                    ExchangeRates = Data["rates"]
                    try:
                        TargetExchangeRate = ExchangeRates[Target]
                        return TargetExchangeRate
                    except KeyError:
                        raise InvalidTargetCurrencyError
                except KeyError:
                    raise UnexpectedResponseError
            except ValueError as exc:
                raise UnexpectedResponseError(
                    "Frankfurter returned a result we couldn't understand"
                ) from exc
        elif response.status_code == 404:
            raise InvalidBaseCurrencyError


def FormatUserInput(RawInput: str) -> tuple[str, str, int]:
    """
    Formats the user input into three usable variables
    Possible Errors:
        InvalidTargetCurrencyError,
        InvalidAmountError,
        UserInputError
    """
    try:
        Base, Amount, Target = RawInput.split(" ", 2)
        if len(Target.split()) != 1:
            raise InvalidTargetCurrencyError
        try:
            IntAmount = int(Amount)
        except ValueError:
            raise InvalidAmountError
        else:
            return Base, IntAmount, Target
    except ValueError:
        raise UserInputError


def FormatOutput(Base: str, Target: str, Amount: int, Exchanged: float) -> str:
    formattedoutput = f"{Amount} in {Base} is converted to {Exchanged} in {Target}"
    return formattedoutput


def run() -> None:
    """
    The main program
    """
    while True:
        try:
            Base, Amount, Target = FormatUserInput(
                input(
                    "how much of which currency do you have? What do you want to convert it to?:"
                ).strip()
            )

            print(
                FormatOutput(
                    Base,
                    Target,
                    Amount,
                    ConvertCurrency(Amount, FetchExchangeRate(Base, Target)),
                )
            )
        except NetworkError:
            print("Something went wrong with your network or the API!")
        except InvalidAmountError:
            print("Invaid 'amount' value!")
        except InvalidBaseCurrencyError:
            print("Invalid Base Currency!")
        except InvalidTargetCurrencyError:
            print("Invalid Target Currency!")
        except UserInputError:
            print("Something is wrong with your input format!")
        except UnexpectedResponseError as exc:
            print(f"Something went wrong: {exc}")

        again = input("Do you want to query another city? (y/n): ").strip().lower()
        if again != "y":
            break


def main():
    run()


if __name__ == "__main__":
    main()
