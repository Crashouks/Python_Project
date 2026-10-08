from app import RouteApp


def main():
    try:
        RouteApp().run()
    except (KeyboardInterrupt, EOFError):
        print("\nПрограму перервано.")


if __name__ == "__main__":
    main()