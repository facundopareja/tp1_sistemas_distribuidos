from distance_calculator import DistanceCalculator


def main():
    query_handler = DistanceCalculator("airport_registers",
                                       "distance_calculation",
                                       "output_2")
    query_handler.run()


if __name__ == '__main__':
    main()
