from App .gui.app import SimulationApp
def main():
    print("[+] Starting Program")
    app = SimulationApp(
        generation_steps=6000,
        population_size=50,
        food_amount=50,
        world_height=1080,
        world_width=1920,
        respawn_food_size=5,
        respawn_food_rate=20,
        fov=90,
        max_distance=200,
        rays=10,
        starting_mutation_rate=0.04,
        starting_mutation_strength=0.05,
        starting_dna=None,
        GUI=False
        )
    app.run()


if __name__ == "__main__":
    main()