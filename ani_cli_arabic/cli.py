"""Command-line interface for ani-cli-arabic."""

import sys
import argparse
import subprocess

from ani_cli_arabic.providers.registry import get_provider, list_providers


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ani-cli-arabic",
        description="Stream Arabic-dubbed/subbed anime from the terminal.",
    )
    parser.add_argument("query", nargs="?", help="Anime title to search for")
    parser.add_argument(
        "-p",
        "--provider",
        default="animeiat",
        choices=list_providers(),
        help="Provider to use (default: animeiat)",
    )
    parser.add_argument(
        "-e",
        "--episode",
        type=int,
        default=None,
        help="Episode number to stream directly",
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List available providers and exit",
    )
    # Personal addition: auto-play the stream URL with mpv instead of just printing it
    parser.add_argument(
        "--play",
        action="store_true",
        default=True,  # I always want auto-play; set False if you just want the URL printed
        help="Automatically open the stream URL with mpv (default: True)",
    )
    return parser


def pick(items: list, label: str) -> object:
    """Prompt the user to pick one item from a numbered list."""
    if not items:
        print(f"No {label} found.")
        sys.exit(1)
    for i, item in enumerate(items, 1):
        print(f"  {i}) {item}")
    while True:
        try:
            choice = int(input(f"Select {label} [1-{len(items)}]: "))
            if 1 <= choice <= len(items):
                return items[choice - 1]
        except (ValueError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_providers:
        print("Available providers:")
        for name in list_providers():
            print(f"  - {name}")
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    provider = get_provider(args.provider)

    print(f"Searching '{args.query}' on {args.provider} …")
    results = provider.search(args.query)
    if not results:
        print("No results found.")
        sys.exit(1)

    anime = pick(results, "anime")
    print(f"\nSelected: {anime}")

    episodes = provider.get_episodes(anime)
    if not episodes:
        print("No episodes found for this anime.")
        sys.exit(1)

    if args.episode is not None:
        matched = [ep for ep in episodes if ep.number == args.episode]
        if not matched:
            print(f"Episode {args.episode} not found.")
            sys.exit(1)
        episode = matched[0]
    else:
        print()
        episode = pick(episodes, "episode")

    print(f"\nFetching stream for {episode} …")
    url = provider.get_stream_url(episode)
    if not url:
        print("Could not retrieve stream URL.")
        sys.exit(1)

    print(f"\nStream URL:\n  {url}")

    if args.play:
        print("\nLaunching mpv …")
        subprocess.run(["mpv", url], check=False)
