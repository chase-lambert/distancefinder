# distancefinder
Final Project for Harvard's CS50 course built with Python using Flask. You can find the actual app at: https://distancefinder.onrender.com/ (Please note, the app is deployed on render's free tier so might be slow on first load as it wakes up.)

My parents were going on a big road trip across America in their new RV. My dad and I decided to build a cool sign post for my mom's Christmas present that had various locations showing places where the family had lived before or currently lives with the distances from the location. It's hard to describe but you see these kinds of things at fun little beach resorts.

Here is how it turned out: 

<p float="left">
  <img src="https://github.com/Chase-Lambert/distancefinder/blob/main/signs.jpg" width="225" height="225" >
  <img src="https://github.com/Chase-Lambert/distancefinder/blob/main/signs-2.jpg" width="225" height="225" >
  <img src="https://github.com/Chase-Lambert/distancefinder/blob/main/signs-3.jpg" width="225" height="225" >
</p>

Each location sign had a little blank space where we sprayed this cool chalkboard spray paint that allows us to write the various distances with chalk at each new location.

I thought it would be a fun idea to write an app to allow my mom to enter their current location and get all the respective distances to fill in the sign post. 

While I hardcoded the actual locations they knew they were going to camp at I also gave her the ability to dynamically enter whatever location they are currently at and it still works.

I called out to an API to grab the various latitude and longitude coordinates for all the locations, including the dynamically added ones, and then used the Haversine Formula (https://en.wikipedia.org/wiki/Haversine_formula) to calculate the distances.

The app was originally deployed using Heroku's free service but they recently shut it down. Thankfully, I was able to migrate to render with minimal fuss (unfortunately a lot of my custom css design did not transfer over and I have not had time to track the bug down.)

My mom has been using the app the last few years and it has worked flawlessly. Overall, it was a super fun project and I count it as a big success as my first real world deployed app.

