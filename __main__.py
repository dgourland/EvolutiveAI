from App .gui.app import SimulationApp
import os, json
SAVE_DIR="./save"

def save(SAVE_PATH:str, config:dict)->None:
    if not os.path.exists(SAVE_PATH):        
        os.mkdir(SAVE_PATH)
    if not os.path.exists(SAVE_PATH+"/config.json"):
        with open(SAVE_PATH+"/config.json", "w") as f:
            f.write(json.dumps(config))

def main()->None:
    print("[+] Starting Program")
    SAVE_NAME="default"
    SAVE=f"./saves/{SAVE_NAME}"
    if (os.path.exists(SAVE)) and (os.path.exists(SAVE+"/config.json")):
        with open(SAVE+"/config.json", "r") as f:
            config_data = json.loads(f.read())

        isgui=True
        app= SimulationApp(
            generation_steps=config_data["generation_steps"],
            population_size=config_data["population_size"],
            food_amount=config_data["food_amount"],
            world_height=config_data["world_height"],
            world_width=config_data["world_width"],
            respawn_food_size=config_data["respawn_food_size"],
            respawn_food_rate=config_data["respawn_food_rate"],
            starting_mutation_rate=float(config_data["starting_mutation_rate_percent"])/100,
            starting_mutation_strength=float(config_data["starting_mutation_strength_percent"])/100,
            GUI=isgui,
            SAVE_PATH=SAVE

        )
    else:
        app = SimulationApp(
            generation_steps=6000,
            population_size=40,
            food_amount=50,
            world_height=1080,
            world_width=1920,
            respawn_food_size=10,
            respawn_food_rate=20,
            starting_mutation_rate=0.04,
            starting_mutation_strength=0.05,
            GUI=True
            )
    try:
        app.run()
    except KeyboardInterrupt:
        save(SAVE, app.export_config())
        
        



if __name__ == "__main__":
    main()