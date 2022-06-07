import requests
import pygame
import io
import itertools
import time


def load_image_from_api(url):
    image_str = requests.get(url).content
    image_file = io.BytesIO(image_str)
    image = pygame.image.load(image_file)
    return image


def draw(picture):
    screen.fill((0, 0, 0))
    screen.blit(picture, (20, 20))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit


if __name__ == "__main__":
    result = requests.get("http://127.0.0.1:8000/api/movie.list?per_page=300&page=1")
    result = result.json()["movies"]
    posters = []
    for r in result:
        posters.append(r["poster"])
    pygame.init()
    screen = pygame.display.set_mode((340, 493), pygame.RESIZABLE)
    images = []
    for poster in posters:
        new_image = load_image_from_api(poster)
        images.append(new_image)
        draw(new_image)
        time.sleep(0.2)

    poster_circle = itertools.cycle(images)
    for poster in poster_circle:
        draw(poster)
        time.sleep(0.5)
