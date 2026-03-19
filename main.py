from game import *
if __name__ == '__main__':
    try:
        g = Game()
        g.run()
    finally:
        pygame.quit()
        sys.exit()