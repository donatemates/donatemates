"use strict";
const AWS = require('aws-sdk');

const encryptedAccessKey = process.env['AccessKey'];
let decryptedAccessKey;
const encryptedSecretKey = process.env['SecretKey'];
let decryptedSecretKey;


function processEvent(event, context, callback) {
    var DynamoBackup = require('dynamo-backup-to-s3');

    var backup = new DynamoBackup({
        includedTables: ['production.campaigns.donatemates', 'production.donations.donatemates'],
        readPercentage: .25,
        bucket: 'donatemates-production-backup',
        stopOnFailure: true,
        base64Binary: true,
        awsAccessKey: decryptedAccessKey,
        awsSecretKey: decryptedSecretKey,
        awsRegion: 'us-east-1'
    });

    backup.on('error', function(data) {
        console.log('Error backing up ' + data.table);
        console.log(data.err);
    });

    backup.on('start-backup', function(tableName, startTime) {
        console.log('Starting to copy table ' + tableName);
    });

    backup.on('end-backup', function(tableName, backupDuration) {
        console.log('Done copying table ' + tableName);
    });

    backup.backupAllTables(function() {
        console.log('Finished backing up DynamoDB');
    });
}

exports.handler = (event, context, callback) => {
    if (decryptedSecretKey) {
        processEvent(event, context, callback);
    } else {
        // Decrypt code should run once and variables stored outside of the function
        // handler so that these are decrypted once per container
        const kms = new AWS.KMS();
        kms.decrypt({ CiphertextBlob: new Buffer(encryptedAccessKey, 'base64') }, (err, data) => {
            if (err) {
                console.log('Decrypt error:', err);
                return callback(err);
            }
            decryptedAccessKey = data.Plaintext.toString('ascii');
            processEvent(event, context, callback);
        });
        kms.decrypt({ CiphertextBlob: new Buffer(encryptedSecretKey, 'base64') }, (err, data) => {
            if (err) {
                console.log('Decrypt error:', err);
                return callback(err);
            }
            decryptedSecretKey = data.Plaintext.toString('ascii');
            processEvent(event, context, callback);
        });
    }
};