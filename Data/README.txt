-------------------
GENERAL INFORMATION
-------------------
1. Title:
Dataset of RTT latency internet measurements in Europe.

2. Description of the dataset:
This dataset provides real-world Round-Trip Time (RTT) latency measurements collected from a distributed network of probing nodes (Monitors) to target IP addresses. It is designed for training and evaluating machine learning models for IP geolocation.

3. Authors:
Miguel A. Ortega, Alejandro S. Martínez-Sala, María-Dolores Cano, Pilar Manzanares-López, Antonio J. Jara.

4. Author's contact information:
Miguel A. Ortega (miguelangel.ortega@edu.upct.es, ORCID: 0009-0000-4420-9672, Universidad Politécnica de Cartagena).

5. Date of data collection:
27 Nov 2024 - 30 Jan 2025: Data collection for Landmark_RTTfingerprint_dataset.csv
27 Nov 2024 - 30 Jan 2025: Data collection for Target_RTTfingerprint_dataset.csv

6. Geographic location of data collection:
The RTT latency measurements were collected from six distributed Monitors, deployed as virtual machines across Azure regions in Madrid (Spain), Dublin (Ireland), Frankfurt (Germany), Warsaw (Poland), Gävle (Sweden), and Milan (Italy).

7. Funding:
This research has been founded by the project R&D&I Lab in Cybersecurity, Privacy, and Secure Communications (TRUST Lab), financed by the European Union NextGeneration-EU, the Recovery Plan, Transformation and Resilience, through INCIBE.

8. Language of the dataset:
English

----------------------------------
SHARING/ACCESS/CONTEXT INFORMATION
----------------------------------
1. Usage Licenses/restrictions placed on the data:
CC-BY 4.0

--------------------
DATA & FILE OVERVIEW
--------------------
1. File List:
	- Landmark_RTTfingerprint_dataset: Learning dataset (contains known IP locations).
	- Target_RTTfingerprint_dataset: Evaluation dataset (contains IP locations known but treated as unknown for model testing).

2. File format:
	.csv

--------------------------
METHODOLOGICAL INFORMATION
--------------------------
1. Description of methods used for collection/generation of data:
Data were gathered via six geographically dispersed Monitors, each issuing bursts of ICMP echo requests to two classes of destinations:
    - Landmarks, whose precise locations are known and used for model training
    - Targets, whose locations are held out and used only for evaluating estimation accuracy

The Monitors were located in the following cities across Europe (format: COUNTRY, CITY, [LAT, LON]):
    - Monitor 1: Spain, Madrid, [40.4153, -3.694]
    - Monitor 2: Ireland, Dublin, [53.3382, -6.2591]
    - Monitor 3: Germany, Frankfurt, [50.1169, 8.6837]
    - Monitor 4: Poland, Warsaw, [52.22977, 21.01178]
    - Monitor 5: Sweden, Gävle, [60.67491, 17.14137]
    - Monitor 6: Italy, Milan, [45.46434, 9.18855]

The resulting measurements were organized into two datasets:
    - Learning Dataset (Landmark_RTTfingerprint_dataset.csv)
Contains RTT measurements to Landmark IPs, used for model training.

    - Validation Dataset (Target_RTTfingerprint_dataset.csv)
Contains RTT measurements to Target IPs, used only for model evaluation purposes. Ground-truth country codes and latitude/longitude are included solely for post-inference accuracy assessment and are not used as model inputs.

-------------------------
DATA-SPECIFIC INFORMATION
-------------------------
Landmark_RTTfingerprint_dataset.csv
	1. Number of variables: 30
	2. Number of cases/rows: 35493
	3. Variable List:
	- measure_id: Unique identifier for each measurement.
	- landmark_id: ID of the geolocated node used as landmark for learning model purposes.
        - landmark_type: Type of landmark (dns, ripe_anchor, ripe_probe)
	- dst_ip: IP address of the landmark.
	- init_time: Timestamp of the measurement.        
	- country_code_gt: Ground truth country code of the landmark.
        - latitude_gt: Ground truth latitude of the landmark.
        - longitude_gt: Ground truth longitude of the landmark.
        - 4h_time_slot: 4-hour time window in which the measurement was taken.
        - 6h_time_slot: 6-hour time window in which the measurement was taken.
	- mean_latency_m1 to mean_latency_m6: mean RTT fingerprint vector (latency measurements from 6 Monitors) (milliseconds).
	- geomean_latency_m1 to geomean_latency_m6: geometric mean RTT fingerprint vector (milliseconds).
	- std_latency_m1 to std_latency_m6: standard deviation of RTTs of each Monitor in fingerprint vector format (milliseconds).
	
Target_RTTfingerprint_dataset.csv
	1. Number of variables: 30
	2. Number of cases/rows: 21738
	3. Variable List:
	- measure_id: Unique identifier for each measurement.
	- target_id: ID of the target node used for validation purposes.
        - target_type: Type of target (dns, ripe_anchor, ripe_probe)
	- dst_ip: IP address of the node.
	- init_time: Timestamp of the measurement.
        - country_code_gt: Ground truth country code of the target node.
        - latitude_gt: Ground truth latitude of the target node.
        - longitude_gt: Ground truth longitude of the target node.
        - 4h_time_slot: 4-hour time window in which the measurement was taken.
        - 6h_time_slot: 6-hour time window in which the measurement was taken.
	- mean_latency_m1 to mean_latency_m6: mean RTT fingerprint vector (latency measurements from 6 Monitors) (milliseconds).
	- geomean_latency_m1 to geomean_latency_m6: geometric mean RTT fingerprint vector (milliseconds).
	- std_latency_m1 to std_latency_m6: standard deviation of RTTs of each Monitor in fingerprint vector format (milliseconds).