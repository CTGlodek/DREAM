#initial code with circle clustering with white ACTIVE fov
import pygame
import random
import math
import numpy as np
from sklearn.cluster import KMeans

# Constants
GRID_WIDTH = 400 # initial 800
GRID_HEIGHT = 400 # initial 600
CLUSTER_COUNT = 2 # initial 5
SENSORS_PER_CLUSTER = 2 # initial 20
SENSOR_RADIUS = 30  # Sensor radius (Rs)  # initial 20
FOV_ANGLE = 30  # Field of view in degrees
NEIGHBORHOOD_DISTANCE = 150  # Neighborhood distance for sensor coverage
ACTIVE_FOV_COLOR = (255, 0, 255, 100)  # Transparent Red (updated color) # initial color (255, 0, 0, 100)
INACTIVE_FOV_COLOR = (255, 215, 0, 100)  # Transparent Yellow
NUM_DIRECTIONS = 4  # Number of discrete directions (0°, 90°, 180°, 270°)
# Constants for colors
SLEEP_MODE_COLOR = (100, 100, 100)  # Dark Gray for sleep mode sensors


# Adjustable variables
TARGET_SPEED = 1.1  # Initial target movement speed # initially 1
TARGET_COUNT = 2  # Update to have 10 targets
TARGET_VELOCITY = 1  # Initial target velocity
SENSOR_SPEED = 2  # Initial sensor movement speed
INITIAL_ENERGY_LEVEL = 1000  # Initial energy level for each sensor
AWAKE_ENERGY_CONSUMPTION_RATE = 0.1  # Energy consumption rate per time slot when awake
TRACKING_ENERGY_CONSUMPTION_RATE = 0.3  # Energy consumption rate per time slot when tracking
LOW_BATTERY_THRESHOLD = 10  # Battery level below which the battery starts blinking
TARGET_COVERAGE_DISTANCE = 100  # Distance within which sensors can cover targets
max_communication_range = 300  # Define the maximum communication range for cluster heads
num_clusters = 20
cluster_head_rotation_frequency = 10  # Replace 10 with the desired rotation frequency

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
pygame.display.set_caption("2D Environment")

# Generate random clusters and distribute sensors within each cluster
# Function to create clusters and distribute sensors within each cluster
def create_clusters():
    clusters = []
    cluster_size = (GRID_WIDTH // CLUSTER_COUNT, GRID_HEIGHT)
    for i in range(CLUSTER_COUNT):
        cluster_x = i * cluster_size[0]
        cluster_rect = pygame.Rect(cluster_x, 0, cluster_size[0], cluster_size[1])
        clusters.append(cluster_rect)
    return clusters

# Function to generate random clusters and distribute sensors within each cluster
def create_sensors(clusters):  # Pass 'clusters' as an argument
    sensors = []
    sensor_positions = []  # Create an empty list to store sensor positions
    total_sensors = CLUSTER_COUNT * SENSORS_PER_CLUSTER
    sensors_per_cluster = [SENSORS_PER_CLUSTER] * CLUSTER_COUNT

    # If the total number of sensors is not evenly divisible by the number of clusters,
    # distribute the remainder sensors among the clusters
    remainder = total_sensors % CLUSTER_COUNT
    for i in range(remainder):
        sensors_per_cluster[i] += 1

    for i, cluster in enumerate(clusters):
        cluster_width = cluster.width
        cluster_height = cluster.height
        num_sensors = sensors_per_cluster[i]

        for j in range(num_sensors):
            x = random.randint(cluster.left + SENSOR_RADIUS, cluster.right - SENSOR_RADIUS)
            y = random.randint(cluster.top + SENSOR_RADIUS, cluster.bottom - SENSOR_RADIUS)

            # Check for overlapping with previously placed sensors
            while any(np.linalg.norm(np.array([x, y]) - np.array([s["x"], s["y"]])) < SENSOR_RADIUS * 2 for s in sensors):
                x = random.randint(cluster.left + SENSOR_RADIUS, cluster.right - SENSOR_RADIUS)
                y = random.randint(cluster.top + SENSOR_RADIUS, cluster.bottom - SENSOR_RADIUS)

            sensors.append({"x": x, "y": y, "angle": random.randint(0, 359), "active_fov": FOV_ANGLE,
                            "detected_targets": [], "energy": INITIAL_ENERGY_LEVEL, "active": False, "cluster": i + 1})
            sensor_positions.append((x, y))  # Append the sensor position to the list
        
    return sensors, sensor_positions  # Return both the sensors list and sensor_positions list


# Function to perform K-Means clustering on sensor positions
def perform_kmeans_clustering(sensor_positions, num_clusters):
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    cluster_labels = kmeans.fit_predict(sensor_positions)
    return cluster_labels

def identify_cluster_heads(sensors, cluster_labels):
    cluster_heads = {}
    for cluster_id in np.unique(cluster_labels):
        indices = np.where(cluster_labels == cluster_id)[0]
        cluster_sensors = [sensors[i] for i in indices]
        cluster_head = max(cluster_sensors, key=lambda sensor: sensor["energy"])
        cluster_heads[cluster_id] = cluster_head
        cluster_head["is_cluster_head"] = True  # Set the flag for the cluster head sensor
    return cluster_heads

# Function to rotate cluster heads within each cluster based on the highest remaining energy
def rotate_cluster_heads(cluster_heads, sensors):
    # Keep track of cluster IDs that already have a cluster head
    clusters_with_head = set()

    # Sort sensors by energy in descending order
    sorted_sensors = sorted(sensors, key=lambda sensor: sensor["energy"], reverse=True)

    for sensor in sorted_sensors:
        cluster_id = sensor["cluster"]
        if cluster_id not in clusters_with_head and sensor["active"]:
            cluster_head = cluster_heads.get(cluster_id)
            if cluster_head and cluster_head != sensor:
                cluster_head["is_cluster_head"] = False
            sensor["is_cluster_head"] = True
            cluster_heads[cluster_id] = sensor
            clusters_with_head.add(cluster_id)

        # If all clusters have a cluster head, break out of the loop
        if len(clusters_with_head) == num_clusters:
            break


# Function to update sensor angles and active FOV based on the target's position
def update_sensor_fov(target_pos, sensors, targets):
    for sensor in sensors:
        x, y = sensor["x"], sensor["y"]
        angle = math.degrees(math.atan2(target_pos[1] - y, target_pos[0] - x)) % 360
        sensor["angle"] = angle

        # Clear the detected_targets list for the current sensor
        sensor["detected_targets"] = []

        # Loop through all targets and check if they are within the neighborhood distance of the sensor
        for target in targets:
            target_x, target_y = target
            distance_to_target = math.sqrt((x - target_x) ** 2 + (y - target_y) ** 2)

            # Check if the target is within the sensor's 90-degree FOV
            if distance_to_target <= NEIGHBORHOOD_DISTANCE:
                angle_to_target = math.degrees(math.atan2(target_y - y, target_x - x)) % 360

                # Calculate the angle difference between the sensor and the target
                angle_diff = (angle_to_target - angle + 360) % 360

                # Check if the target is within the sensor's 90-degree FOV
                if angle_diff <= 45 or angle_diff >= 315:
                    sensor["detected_targets"].append((target_x, target_y))  # Convert to a tuple
                    sensor["active"] = True
                    break  # Once a target is covered, there's no need to check other targets
                else:
                    # Mark the sensor as inactive and clear the detected_targets list
                    sensor["active"] = False
                    sensor["detected_targets"] = []

# Function to draw each sensor as a disk with lines representing the active FOV
def draw_sensors(sensors, cluster_heads):
    for sensor in sensors:
        x, y, angle, active_fov = sensor["x"], sensor["y"], sensor["angle"], sensor["active_fov"]
        energy = sensor["energy"]
        is_sleeping = not sensor["active"] and sensor.get("is_cluster_head") is None

        # Draw the sensor as a solid blue circle with a black border
        pygame.draw.circle(screen, (0, 0, 255), (x, y), SENSOR_RADIUS)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), SENSOR_RADIUS, 2)

        if sensor["active"] or sensor.get("is_cluster_head"):
            # Draw the active FOV as a filled sector in white color
            angle_start = math.radians(angle - active_fov / 2)
            angle_end = math.radians(angle + active_fov / 2)

            # Use two points to create a triangle to draw the filled sector
            p1 = (x, y)
            p2 = (x + int(SENSOR_RADIUS * math.cos(angle_start)), y + int(SENSOR_RADIUS * math.sin(angle_start)))
            p3 = (x + int(SENSOR_RADIUS * math.cos(angle_end)), y + int(SENSOR_RADIUS * math.sin(angle_end)))

            # Draw the filled sector as a triangle
            pygame.draw.polygon(screen, (255, 255, 255), [p1, p2, p3])

            # Draw line connecting sensor to target within FOV (only if sensor is covering the target)
            for target in sensor["detected_targets"]:
                distance_to_target = math.sqrt((x - target[0]) ** 2 + (y - target[1]) ** 2)
                if distance_to_target <= NEIGHBORHOOD_DISTANCE:
                    pygame.draw.line(screen, (0, 0, 0), (x, y), target, 2)

        # Draw energy level as a battery next to the sensor
        battery_width = 8
        battery_height = SENSOR_RADIUS * 2
        battery_x = x + SENSOR_RADIUS + 5
        battery_y = y - SENSOR_RADIUS
        battery_level = int((energy / INITIAL_ENERGY_LEVEL) * battery_height)

        # Calculate the battery color based on the battery level
        battery_color = (0, 255, 0) if battery_level > 0 else (255, 0, 0)
        pygame.draw.rect(screen, (0, 0, 0), (battery_x, battery_y, battery_width, battery_height), 1)

        if battery_level > 0:
            pygame.draw.rect(screen, battery_color, (
                battery_x + 1, battery_y + battery_height - battery_level + 1, battery_width - 2, battery_level - 2))

        # Check if the sensor is in sleep mode and draw the entire disk in dark gray
        if is_sleeping:
            pygame.draw.circle(screen, SLEEP_MODE_COLOR, (x, y), SENSOR_RADIUS)

        # Check if the sensor is a cluster head and draw the entire disk in pink
        if sensor.get("is_cluster_head"):
            # Draw the filled sector as a triangle for cluster heads
            pygame.draw.polygon(screen, (255, 192, 203), [p1, p2, p3])


# Function to draw the clusters on the screen
def draw_clusters(cluster_labels, sensor_positions, cluster_heads):
    cluster_colors = generate_cluster_colors(np.max(cluster_labels))  # Use the new cluster colors
    cluster_centers = {}

    for cluster_id in np.unique(cluster_labels):
        indices = np.where(cluster_labels == cluster_id)[0]
        cluster_center = np.mean(np.array([sensor_positions[i] for i in indices]), axis=0)
        cluster_centers[cluster_id] = (int(cluster_center[0]), int(cluster_center[1]))

    for cluster_id, center in cluster_centers.items():
        # Check if the cluster has a head and assign a different color to the head
        if cluster_id in cluster_heads:
            pygame.draw.circle(screen, (255, 192, 203), center, int(NEIGHBORHOOD_DISTANCE), 2)  # Pink for cluster head
        else:
            pygame.draw.circle(screen, cluster_colors[cluster_id - 1], center, int(NEIGHBORHOOD_DISTANCE), 2)  # Use the new cluster colors

# Function to generate distinct colors for each target
def generate_target_colors(count):
    return [(0, 0, 0)] * count

def generate_cluster_colors(count):
    colors = []
    for _ in range(count):
        colors.append((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
    return colors

# Function to calculate the custom distance between two sensors' centers
def custom_distance(sensor_position1, sensor_position2, radius):
    x1, y1 = sensor_position1
    x2, y2 = sensor_position2
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) - 2 * radius

# Function to update sensor's detected targets based on target positions
def update_sensor_coverage(sensor, targets):
    x, y = sensor["x"], sensor["y"]
    sensor["detected_targets"] = [(tx, ty) for tx, ty in targets if
                                  math.sqrt((x - tx) ** 2 + (y - ty) ** 2) <= SENSOR_RADIUS]

# Function to perform circle-based clustering on sensor positions
def perform_circle_based_clustering(sensor_positions, radius):
    num_sensors = len(sensor_positions)
    cluster_labels = np.zeros(num_sensors, dtype=int)
    current_cluster_label = 0

    def is_in_circle(sensor_pos1, sensor_pos2, radius):
        distance = np.linalg.norm(np.array(sensor_pos1) - np.array(sensor_pos2))
        return distance <= radius

    for i in range(num_sensors):
        if cluster_labels[i] != 0:
            continue

        current_cluster_label += 1
        cluster_labels[i] = current_cluster_label

        for j in range(i + 1, num_sensors):
            if cluster_labels[j] != 0:
                continue

            if is_in_circle(sensor_positions[i], sensor_positions[j], radius):
                cluster_labels[j] = current_cluster_label

    return cluster_labels

# Function to determine if a sensor should go to sleep mode based on network conditions, target density, or remaining energy levels
def should_sleep(sensor, sensors):
    # If sensor has low energy, put it to sleep
    if sensor["energy"] < LOW_BATTERY_THRESHOLD:
        return True

    # Check if there are nearby sensors with higher energy levels
    nearby_sensors = [other_sensor for other_sensor in sensors if
                      sensor != other_sensor and
                      custom_distance((sensor["x"], sensor["y"]), (other_sensor["x"], other_sensor["y"]), SENSOR_RADIUS) <= NEIGHBORHOOD_DISTANCE and
                      other_sensor["energy"] > sensor["energy"]]

    # If sensor has overlapping neighbors with higher energy, put it to sleep
    if nearby_sensors:
        return True

    # If sensor does not detect any targets and has no nearby sensors, put it to sleep
    if not sensor["detected_targets"]:
        return True

    return False


# Function to generate new targets with the same diagonal path as the previous ones
def generate_new_targets(count):
    new_targets = []
    for i in range(count):
        new_targets.append([random.randint(-SENSOR_RADIUS, GRID_WIDTH // 2),
                            random.randint(-SENSOR_RADIUS, GRID_HEIGHT // 2)])
    return new_targets

# Function to allow sensors to communicate with each other
def communicate_within_cluster(sensor, active_sensors_in_cluster, cluster_heads):
    combined_targets = set(sensor["detected_targets"])  # Convert the list to a set

    # Set a threshold for the number of sensors needed to cover a target
    coverage_threshold = 3

    for other_sensor in active_sensors_in_cluster:
        if other_sensor != sensor and other_sensor["active"]:
            # Combine the detected targets of the current sensor with the others in the same cluster
            combined_targets.update(other_sensor["detected_targets"])  # Use 'update' to add elements to the set

            # Check if the target is covered by more than the coverage threshold
            if len(combined_targets) > coverage_threshold:
                # Put the redundant sensor to sleep mode
                other_sensor["active"] = False
                other_sensor["detected_targets"] = []

    # If the sensor is a cluster head, update its detected targets as well
    if sensor.get("is_cluster_head"):
        for other_cluster_head in cluster_heads.values():
            if other_cluster_head != sensor and other_cluster_head["active"]:
                combined_targets.update(other_cluster_head["detected_targets"])

    # Convert the combined_targets set back to a list and assign it to the sensor dictionary
    sensor["detected_targets"] = list(combined_targets)


def communicate_between_cluster_heads(cluster_heads, max_communication_range):
    for cluster_head in cluster_heads.values():
        combined_targets = set(cluster_head["detected_targets"])  # Convert the list to a set

        # Find neighboring cluster heads within the max communication range
        neighboring_cluster_heads = [other_cluster_head for other_cluster_head in cluster_heads.values() if
                                     other_cluster_head != cluster_head and
                                     custom_distance((cluster_head["x"], cluster_head["y"]),
                                                     (other_cluster_head["x"], other_cluster_head["y"]),
                                                     SENSOR_RADIUS) <= max_communication_range and
                                     other_cluster_head["active"]]

        # Combine the detected targets of the current cluster head with neighboring cluster heads
        for other_cluster_head in neighboring_cluster_heads:
            combined_targets.update(other_cluster_head["detected_targets"])

        # Convert the combined_targets set back to a list and assign it to the cluster head dictionary
        cluster_head["detected_targets"] = list(combined_targets)


# Function to rotate cluster heads within each cluster based on the highest remaining energy
def rotate_cluster_heads(cluster_heads, sensors):
    for cluster_id in range(1, num_clusters + 1):
        active_sensors_in_cluster = [sensor for sensor in sensors if
                                     sensor["cluster"] == cluster_id and sensor["active"]]

        if active_sensors_in_cluster:
            # Find the sensor with the highest remaining energy in the cluster
            highest_energy_sensor = max(active_sensors_in_cluster, key=lambda sensor: sensor["energy"])

            # Set the sensor with the highest energy as the new cluster head
            cluster_head = cluster_heads.get(cluster_id)
            if cluster_head and cluster_head != highest_energy_sensor:
                cluster_head["is_cluster_head"] = False
            highest_energy_sensor["is_cluster_head"] = True
            cluster_heads[cluster_id] = highest_energy_sensor

def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
    pygame.display.set_caption("2D Environment")

    clusters = create_clusters()
    sensors, sensor_positions = create_sensors(clusters)

    # Identify cluster heads and initialize the cluster head rotation counters
    cluster_labels = perform_circle_based_clustering(sensor_positions, NEIGHBORHOOD_DISTANCE)
    cluster_heads = identify_cluster_heads(sensors, cluster_labels)
    cluster_head_rotation_counters = {cluster_id: 0 for cluster_id in range(1, num_clusters + 1)}

    targets = generate_new_targets(TARGET_COUNT)
    target_colors = generate_target_colors(TARGET_COUNT)

    clock = pygame.time.Clock()
    running = True

    testing = False  # used for testing a single target

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for target in targets:
            if testing:
                dt = 0
                keys = pygame.key.get_pressed()
                
                if keys[pygame.K_w]:
                    target[1] -= 1 #* dt
                if keys[pygame.K_s]:
                    target[1] += 1 #* dt
                if keys[pygame.K_a]:
                    target[0] -= 1 #* dt
                if keys[pygame.K_d]:
                    target[0] += 1 # * dt
            else:
                target[0] += TARGET_SPEED * random.uniform(0.5, 3.5) # intially (0.5, 1.5)
                target[1] += TARGET_SPEED * random.uniform(0.5, 3.5) # intially (0.5, 1.5)
                target[0] %= GRID_WIDTH
                target[1] %= GRID_HEIGHT

        for target in targets:
            update_sensor_fov(target, sensors, targets)

        for sensor in sensors:
            update_sensor_coverage(sensor, targets)

        # Update communication between sensors within the same cluster
        for cluster_id in range(1, num_clusters + 1):
            active_sensors_in_cluster = [sensor for sensor in sensors if
                                         sensor["cluster"] == cluster_id and sensor["active"]]
            for sensor in active_sensors_in_cluster:
                communicate_within_cluster(sensor, active_sensors_in_cluster, cluster_heads)

        # Update communication between cluster heads within the max communication range
        communicate_between_cluster_heads(cluster_heads, max_communication_range)

        for sensor in sensors:
            if sensor["active"]:
                energy_consumption_rate = TRACKING_ENERGY_CONSUMPTION_RATE if sensor["detected_targets"] else AWAKE_ENERGY_CONSUMPTION_RATE
                sensor["energy"] = max(sensor["energy"] - energy_consumption_rate, 0)

        screen.fill((255, 255, 255))
        draw_clusters(cluster_labels, sensor_positions, cluster_heads)
        draw_sensors(sensors, cluster_heads)

        for target, color in zip(targets, target_colors):
            pygame.draw.circle(screen, color, target, 8)

        # Rotate cluster heads based on the highest remaining energy
        rotate_cluster_heads(cluster_heads, sensors)

        pygame.display.flip()
        clock.tick(60)

        if not any(-SENSOR_RADIUS <= target[0] <= GRID_WIDTH + SENSOR_RADIUS and
                   -SENSOR_RADIUS <= target[1] <= GRID_HEIGHT + SENSOR_RADIUS for target in targets):
            targets = generate_new_targets(TARGET_COUNT)

    pygame.quit()

if __name__ == "__main__":
    main()