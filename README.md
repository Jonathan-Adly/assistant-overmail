# **Assistant-OverMail**

Assistant-OverMail is an open-source Django application designed to simplify your workflow by emailing assistant@overmail.ai (or any domain name if you self-host) and getting a response back from GPT-4. 

You can use this to use GPT-4 privately, go around employers' blocks, or simply as a short-cut to deal with emails in the inbox. You can try it at: [overmail.ai](https://overmail.ai)

For self-hosting. You will need Docker and Docker Compose for easy setup and deployment. The app integrates with Stripe for fiat payments, OpenNode for Bitcoin payments, and any mailing provider such mailgun, sendgrid, or AWS SES.

## **Updates**

- 2/27/25: Response now come back in markdown

- 2/22/24: You can now respond to the Assistant email for follow up on requests


## **Installation**

Follow these steps to get Assistant-OverMail up and running:



1. Clone the repository:

```
git clone https://github.com/yourgithub/assistant-overmail.git
cd assistant-overmail
```


  2. Set up environment variables:

Copy the `.example.env` file to `.env` or `.dev.env` for development settings.


```
cp .example.env .env
```


3. Launch with Docker Compose:



    * Ensure Docker and Docker Compose are installed on your machine.
    * Build and start the containers in detached mode:


```
docker-compose up -d --build
```



## **Configuration**

After installation, configure the application by setting up the required environment variables in your `.env` or `.dev.env` file. This includes your Stripe API keys, OpenNode API keys, and mailing provider configurations.


## **Usage**

With Assistant-OverMail running, access it through your browser or at localhost:8000. For production we recommend an Nginx and SSL configuration. 


## **Integrations**


### **Stripe**



* Create a Stripe account and obtain your API keys.
* Add your Stripe API keys to your environment file.
* Setup a webhook endpoint


### **OpenNode**



* Sign up for an OpenNode account to handle Bitcoin transactions.
* Configure your OpenNode API keys in the environment file.


### **Mailing Providers**



* Choose a mailing provider (e.g., SendGrid, Mailgun) and set up an account.
* Configure your mailing provider's API keys and settings in the environment file.
* Setup mail receiving webhooks


## **Contributing**

We welcome contributions! 

**License**

Assistant-OverMail is MIT licensed.
