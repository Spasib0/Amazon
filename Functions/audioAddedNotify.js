const https = require('https')
const http = require('http')

exports.handler = async (event) => {
  const secret = process.env.SECRET;
  const serviceName = process.env.SERVICE_NAME;
  const b = Buffer.from(serviceName +':'+secret)
  const auth = 'Basic ' + b.toString('base64');
  
  //console.log(auth)
  
  const options = {
    // host: 'nau-mag.com',
    host : 'school-drozdov.com',
    port : 443,
    path : '/game/service/transcode',
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Accept-Charset': 'utf-8',
        'Authorization': auth
    }
  }
  


const data = {"value" : event.Records[0].s3.object.key}

  const promise = new Promise(function(resolve, reject) {
    
    var req = https.request(options, function(res) {

            if (res.statusCode < 200 || res.statusCode >= 300) {
                return reject(new Error('statusCode=' + res.statusCode));
            }

            var body = [];
            res.on('data', function(chunk) {
                body.push(chunk);
            });

            res.on('end', function() {
                try {
                    body = JSON.parse(Buffer.concat(body).toString());
                } catch(e) {
                    reject(e);
                }
                resolve(body);
            });
        });

        req.on('error', function(err) {
            reject(err);
        });

        req.write(JSON.stringify(data));

        req.end();



    })
  return promise
};
