-- Simple Database Creation Script
-- Create the database and user for the chat application

-- Create the database
CREATE DATABASE chatappdb;

-- Create user with password
CREATE USER demouser WITH PASSWORD '1234ABcd!';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE chatappdb TO demouser;
