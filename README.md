# GuideToExile
A build guide repository for Path of Exile. A place to find someone else's build guide or post you own.

Live website: https://guidetoexile.com

### Main features
 * Very easy importing from Path of Building
 * Displaying the most important data from PoB: statistics, skill trees, gear and skill gems
 * A WYSIWYG guide editor (What You See Is What You Get)
 * Guide draft system
 * Possibility to add Item references in the text editor -> after publishing a tooltip with Item details will be attached
 * Comment section for each guide
 * Liked guide system: your own list of liked guides and a guide popularity ranking
 * Author popularity ranking based on likes
 * Login with social media accounts (Google and Facebook)

### Technical details
Project implemented primarly in Python (Django) with some Lua based integration. Frontend created using Django Templates with some JavaScript.

Project is deployed on AWS, using: EC2, Elastic Beanstalk, RDS (Postgres), Route 53, SES, S3 and Cloudfront.
