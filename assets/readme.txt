# Smart Location System



## Systems Architecture Overview
![assets/Location.png](assets/Location.png)

Before we switch gears into the implementation of this project, let’s first take a closer look at the architecture behind the data pipelines we’re going to build. At the core of our setup, AWS Glue will connect with AWS Kinesis Streams as the source of truth for the data acting as a pipeline for real-time streaming data.

From here, various platforms will process incoming data through transformations and aggregations that could potentially clean, filter, and enrich the data in Kinesis stream. For example, we will apply such transformations to remove sensor readings above a threshold or to aggregate data at time-window intervals to create meaningful insights.

Once the data is processed, it’s routed to a variety of destinations. Those include:

1. PostgreSQL for storing structured, queryable data
2. Amazon S3 for scalable, cost-effective storage of raw and processed data
3. Delta Lake for enhanced data lake capabilities with ACID transactions

## Setting Up the Project
We start by setting up a new project, installing dependencies, and configuring our development environment. For this project, you’ll need:
1. AWS Account

## installing Dependencies

To get AWS working on your computer you will need to install aws-cli . AWS CLI allows you to connect your workload and resources on AWS to your computer.  Choose the right operating system running on your computer, install it and you can verify the installation by running the command below;


```bash
aws --version
```
Of course, you will need python running on your laptop. Once done, you will need boto3 by running pip install boto3 .



Before we head on to producing data to Kinesis Streams, we need to ensure we create the right topics on AWS Kinesis where the sensor data (humidity, temperature and energy ) will be sitting in. To do that, you need to run the command below:

```bash
aws kinesis create-stream --stream-name temp_stream --shard-count 1

aws kinesis create-stream --stream-name energy_stream --shard-count 1

aws kinesis create-stream --stream-name humidity_stream --shard-count 1
```

## Coding the Sensor Data Producer
The first step is to create a data producer that simulates sensor data and sends it to Kinesis Streams. This producer will generate JSON messages that mimic real-time data input. The approach to the data production simulates realtime sensors generating data from multiple sensors where each produces data in parallel and independently. In our case, they each will be running on separate threads;

config.json

The config.json contains list of devices that will be producing data to the Kinesis streams.

producer.py
You can start the producer by running

```bash
python producer.py
```

Here is a high-level step-by-step guide to setting up an AWS-based pipeline for streaming data from Kinesis, transforming it with Glue, storing it in S3, notifying with Lambda and SNS, and finally querying with Athena:

### Step 1: **Set up Kinesis Stream**
1. **Create a Kinesis Data Stream**:
   - In the AWS Management Console, go to **Kinesis**.
   - Create a **Kinesis Data Stream** (give it a meaningful name, e.g., `my-stream`).
   - Set the number of shards based on your expected throughput.

### Step 2: **Create the First Glue Job to Extract Data from Kinesis and Load it into S3**
1. **Create an S3 Bucket for Input Data**:
   - Create an S3 bucket (e.g., `location-datastream-data-bucket`).
   
2. **Create a Glue Job for Streaming Data**:
   - In the AWS Management Console, go to **AWS Glue**.
   - Create a new Glue job with **Python** or **Spark** (PySpark or Scala).
   - **Source**: Use the Kinesis stream as the data source. Set the appropriate stream name (e.g., `my-stream`).
   - **Transformation**: Optionally transform the data if needed (e.g., format conversion, filtering).
   - **Target**: Define the S3 output location (e.g., `s3://location-datastream-data-bucket/`).
   - Set up the Glue job to **run continuously**, or schedule it for periodic execution.

![S3 Bucket Structure](S3.png)

3. **Set up IAM Permissions**:
   - Ensure that the Glue job has the necessary IAM roles/permissions to read from Kinesis and write to S3.

### Step 3: **Create a Glue Job to Extract Data from S3 and Combine into One Final Bucket**
1. **Create a Final S3 Bucket for Combined Data**:
   - Create a final S3 bucket (e.g., `my-final-output-bucket`).

2. **Create a Glue ETL Job for Combining Data**:
   - Create a new Glue job to pull data from the input S3 bucket (`location-datastream-data-bucket`).
   - Perform any necessary transformations to combine the data. You can use Glue’s built-in **DynamicFrame** transformations or Spark transformations (e.g., `join`, `union`, etc.).
   - Write the combined data to the final S3 bucket (`location-datastream-data-bucket`).

3. **Configure Data Format**:
   - Choose the desired output format for the final combined data (e.g., Parquet, CSV, or JSON).

4. **Set up IAM Permissions**:
   - Ensure that the Glue job has the necessary IAM permissions to read from the input S3 bucket and write to the final S3 bucket.

### Step 4: **Set up SNS Topic for Notification**
1. **Create an SNS Topic**:
   - We already created 3 different topics.

2. **Subscribe to the SNS Topic**:
   - Subscribe email, SMS, or another communication channel to the SNS topic for notifications.

### Step 5: **Create Lambda Function to Send Email Notification via SNS**
1. **Create a Lambda Function**:
   - Go to **AWS Lambda** and create a new function.
   - In the function, write the code that will be triggered once the final S3 bucket receives new data.
   - The Lambda function will publish a message to the SNS topic created earlier.
   - Code (Python): publishnotification.py


2. **Set up Lambda Trigger**:
   - Set up a trigger on the **final S3 bucket** (`location-datastream-data-bucket `) to invoke the Lambda function when new data is uploaded.

### Step 6: **Create an S3 Event Notification for Lambda Trigger**
1. **Configure S3 Event Notification**:
   - Go to your **final S3 bucket** (`location-datastream-data-bucket `) in the S3 Console.
   - Create an **event notification** for object creation events (e.g., `s3:ObjectCreated:*`).
   - Set the Lambda function as the destination for the event notification.

### Step 7: **Set up Glue Crawler to Catalog Final Data**
1. **Create a Glue Crawler**:
   - In the **AWS Glue Console**, create a new Glue crawler.
   - Set the **source path** to the final S3 bucket (`s3://location-datastream-data-bucket/`).
   - Choose a database (or create one) to store the metadata.

2. **Run the Glue Crawler**:
   - Run the Glue crawler to catalog the data in the final bucket. This will allow Athena to query the data.

### Step 8: **Set Up Athena to Query the Data**
1. **Go to Athena**:
   - In the AWS Console, navigate to **Athena**.

2. **Configure Athena to Use the Glue Catalog**:
   - Athena uses the Glue Data Catalog as a metastore, so ensure that Athena is configured to use the database created by the Glue Crawler.

3. **Write SQL Queries**:
   - Use Athena to write SQL queries against the data stored in the final S3 bucket (now cataloged by Glue).

### Step 9: **Monitor and Test the Pipeline**
1. **Test the Kinesis to S3 Pipeline**:
   - Start sending data to the Kinesis stream and verify it appears in the input S3 bucket.
   
2. **Verify Glue Jobs**:
   - Ensure the Glue jobs for combining data are running correctly and outputting to the final S3 bucket.

3. **Verify Lambda Notification**:
   - Upload test data to the final S3 bucket and ensure the Lambda function sends an SNS notification when new files are added.

4. **Run Athena Queries**:
   - After the Glue Crawler has indexed the final data, run Athena queries to validate the data is queryable.

---

### Summary:
- **Kinesis** captures and streams data.
- **First Glue Job** extracts data from Kinesis and writes to an S3 bucket.
- **Second Glue Job** processes and combines data from S3 into a final S3 bucket.
- **Lambda Function** sends an SNS notification when new data is loaded to the final S3 bucket.
- **Glue Crawler** catalogs the data in the final S3 bucket for querying.
- **Athena** enables you to query the cataloged data stored in S3.

This architecture ensures data flows from Kinesis to S3, is processed and combined via Glue, and is then made accessible via Athena for querying. Lambda and SNS add an automated notification step for tracking the load process.

