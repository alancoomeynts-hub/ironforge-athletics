# IronForge Athletics

## UX

### Primary Goal
IronForge Athletics is a modern support and membership platform for a local gym. Its primary purpose is to attract new 
members by helping them understand the gym’s services and choose the membership that best suits their goals. It also provides
existing members with access to fitness and nutrition resources, member-only discounts in the online shop, and opportunities 
to engage with the wider IronForge community.

The central offering is a full gym membership. Alongside membership access, the platform provides:

- Exercise and nutrition plans.
- An online shop selling fitness and nutrition products, as well as branded IronForge Athletics merchandise. The shop is open
to everyone, although gym members receive exclusive discounts.
- Product reviews from customers.
- Member profiles.
- Community progress updates, where members can share their achievements and experiences.

### Business Needs
- Promote the local gym, its facilites and services.
- Convert visitors into gym members through a clear and secure subscription process.
- Provide access to fitness and nutrition resources.
- Provide member-only discounts in the online shop.
- Build a supportive and engaged fitness community.
- Encourage members to share their experiences and achievements.
- Provide Administrative tools for managing the platform, memberships, products, product reviews, users and subscription payments.

### User Needs
#### Potential Gym Members:
- Understand the gym’s facilities, services, location, and training environment.
- Compare membership options, prices, benefits, and included services.
- Register for an account and complete a secure membership subscription.
- Decide confidently whether IronForge Athletics suits their goals and experience level.

#### Gym Members:
- Log in securely and view their membership and subscription details.
- Access member-only exercise and nutrition resources.
- Access the external class-booking application through a clear link.
- View gym message board for announcements and community updates.
- Manage their profile and share their fitness progress.
- Purchase products or branded merchandise and review eligible purchases.
 
Note: Class scheduling will be handled by third-party appointment scheduling software outside of the IronForge Athletics platform.

#### Shop Customers:
- Be able to browse products
- View product details including price, description.
- Be able to add the product to their cart.
- Be able to view their cart and checkout.
- Be able to view their order history.
- Complete the checkout process anonymously or with a registered account.

#### Community Users

Registered community users need to:

- Access a welcoming and motivating online community.
- Share fitness achievements and progress updates.
- Interact positively with other users.


#### Administrators

Administrators need to:

- Manage users, memberships, subscriptions, products, orders, and reviews.
- Create and update membership, exercise, and nutrition plans.
- Manage product categories, images, prices, and stock information.
- Moderate reviews and community progress updates.
- Publish gym announcements and maintain class-booking information.



### Agile Planning

#### User Stories
1. As a potential gym member, I want to learn about the gym's facilities and services so I can decide whether IronForge Athletics is right for me.
2. As a potential gym member, I want to register for an account.
3. As a potential gym member, I want to view my membership details so I can compare membership options and decide whether IronForge Athletics is right for me.
4. As a potential gym member, I want to subscribe to a membership so I can access fitness and nutrition resources.
5. As a gym member, I want to view my subscription details so I can edit or cancel my subscription.
6. As a gym member, I want to view and edit my profile so I can share my fitness progress, review past shop orders.
7. As a gym member, I want to view a gym message board so I can stay informed about the gym's activities and community, and share my fitness achievements with other members.
8. As a shop customer, I want to browse products so I can find the products interest me.
9. As a shop customer, I want to view product details so I can decide whether to purchase the product.
10. As a shop customer, I want to add the product to my cart so I can purchase multiple products at once.
11. As a shop customer, I want to view my cart so I can review my order before checkout.
12. As site administrator, I want to be able to manage users, memberships, products, shop orders, and the message board.

#### Issues
1. **Marketing:** Implement public marketing pages that clearly describe IronForge Athletics’ facilities, services, location, and training environment.
###### Features:
- Present gym information in a clear and concise manner, pages to implements include:
- Home: Hero image, with call to action to register for a membership.
- About:gym story, ethod, teams and photos.
- Facilities & Services: equipment, classes, opening hours, location/map, contact details and form.
- Membership overview: description of plans and benefits.

##### Acceptance Criteria:
- All pages are accessible from the main navigation.
- Content clearly explains what the gym offers and who it’s for.
- Clear CTAs to “View Memberships” and “Register”.
- Location and contact information are easy to find.
- Pages render consistently with site branding on desktop and mobile.  

2. **User Registration:** Implement user registration so potential members can create an account.
###### Features:

- Registration form (username, email, password, password confirmation).
- Email verification (if using allauth) or basic email-based flow.
- Automatic creation of UserProfile on registration.
- Redirect to a “home" after registration.

###### Acceptance criteria:

- Users can register with a valid email and password.
- UserProfile is created automatically for new users.
- New users receive an email with a verification link.

3. **Membership Plans Listing and Comparison:** Implement a membership plans page where potential members can view and 
compare all available membership options.
###### Features:
- List all active `MembershipPlan` objects.
- Display the following information for each plan:
  - Name.
  - Description.
  - Price.
  - Billing interval
  - Key benefits and features.
- Provide a clear visual comparison using Bootstrap cards.
- Include "Join Now" button that redirects to;
  - **Subscribe**, for authenticated users.
  - **Register** or **Log in**, for users who are not authenticated.
  - 
##### Acceptance Criteria

-  All active membership plans are displayed on a dedicated public page.
-  Plan names, descriptions, prices, billing intervals, benefits, and features are clear and accurate.
-  The page provides an easy-to-understand visual comparison of the available plans.
- The page is accessible throughout the site.
- Non-authenticated users can view all membership plans.
- Non-authenticated users are prompted to register or log in before subscribing.
- Authenticated users can proceed to subscribe to their selected plan.

4. **Membership Subscription:** Implement a membership subscription flow that allows users to become members through Stripe.
##### Features

- Allow users to select a membership plan from the available `MembershipPlan` objects.
- Provide a checkout page that creates a Stripe Customer and Subscription.
- On successful payment, create or update a `Membership` record with:
  - `user`
  - `plan`
  - `stripe_subscription_id`
  - `status = 'active'`
  - `current_period_end`
- Redirect successful subscribers to a confirmation or member welcome page.
- Grant access to member-only areas, such as the community and member plans, when the membership becomes active.

##### Acceptance Criteria

- Logged-in users can select a membership plan and complete the subscription process through Stripe.
- Successful payment creates or updates a `Membership` record with the correct data.
- Users gain access to member-only sections immediately after successful signup.
- Failed payments display clear error messages and do not create an active membership.

5. **Manage Membership:** Implement a member area page where users can view and manage their active membership and subscription.

### Features

- Display the current membership plan, subscription status, next billing date, and billing amount.
- Provide a link to the Stripe Customer Portal, or implement a basic cancellation and update flow through the Stripe API.
- Clearly explain what happens when a subscription is cancelled, including whether access continues until the end of the current billing period.
- Optionally allow users to upgrade or downgrade their plan through Stripe.

### Acceptance Criteria

- Logged-in members can view their current subscription details.
- Members can cancel or update their subscription through Stripe or the Stripe Customer Portal.
- Cancellation updates the local `Membership` status through a webhook.
- The interface clearly communicates the subscription state and next billing date.

6. **View and edit profile:** Implement member profile pages where users can view and edit their personal information and access their progress updates and shop orders.

### Features

#### Profile View

Display the following information:

- Username.
- Bio.
- Goals.
- Fitness level.
- Membership status.
- The user's `ProgressUpdate` entries, or a link to view them.
- A link to the user's shop order history.

#### Profile Edit

Provide a form that allows users to update:

- Bio.
- Goals.
- Fitness level.

### Acceptance Criteria

- Members can view their own profile with all relevant information.
- Members can edit their profile details through a form.
- The profile page includes links or sections for progress updates and order history.
- Profile changes are saved and reflected immediately.

7. **View and participate in community forums:** Implement a gym message board where members can view announcements, 
discuss topics, and share fitness achievements.

### Features

- Implement `Category`, `Thread`, and `Post` models.
- Provide at least the following categories:
  - **Announcements**, with posting restricted to administrators.
  - **General** or **Progress & Achievements**, where members can participate.
- Provide a thread list for each category.
- Provide thread detail pages displaying posts.
- Allow members to:
  - Create threads in permitted categories.
  - Post replies.
  - Share progress updates and achievements through threads and posts.
- Restrict forum access to active members.

### Acceptance Criteria

- Active members can view and participate in the forum.
- Administrators can create announcements that are visible to all members.
- Members can create threads and posts in appropriate categories.
- Non-members cannot access the forum.

8. Browse Products: Implement a product catalog page where visitors and members can browse available products.

##### Features

- Provide a product list displaying:
  - Product name.
  - Price.
  - Main image.
  - Short description.
- Add basic filtering, such as filtering by nutrition, fitness, or merchandise.
- Make the catalog publicly accessible without requiring login.
- Indicate member-only pricing where applicable.

##### Acceptance Criteria

- All active products are visible in the catalog.
- Users can filter products or clearly distinguish between product types.
- The product list is readable and navigable on mobile and desktop devices.
- Each product card contains a clear link to its product detail page.

9. View Product Details:
Implement product detail pages with the information customers need to make purchase decisions.

##### Features

Display the following information:

- Product name.
- Price.
- Full description.
- Product images.
- Member and non-member prices, if discounts apply.
- Reviews, once the review functionality is implemented.
- An **Add to cart** button.

##### Acceptance Criteria

- Product detail pages render correctly for all active products.
- All key information, including price, description, and images, is visible.
- The **Add to cart** button is present and functional.

10. Add Products to the Cart: 
Implement add-to-cart functionality that allows users to collect multiple products before checkout.

##### Features

Implement `Cart` and `CartItem` models supporting:

- Anonymous carts stored in the session.
- Carts associated with logged-in users.
- Adding products from product detail and product list pages.
- Cart item quantity management, including incrementing the quantity when a product is already in the cart.

##### Acceptance Criteria

- Users can add products to the cart from product pages.
- The cart correctly reflects added products and quantities.
- Anonymous users retain cart contents through their session.
- When an anonymous user logs in, their cart is merged into their user cart.



11. View and Manage the Cart: Implement a cart page where users can review and manage their selected items before checkout.

##### Features

The cart page must show:

- A list of items, including product, quantity, price, and line total.
- Cart subtotal.
- Any applicable discounts.
- Cart total.

Users must be able to:

- Update item quantities.
- Remove items.
- Proceed to checkout through a clear call to action.

##### Acceptance Criteria

- Users can view their cart contents and totals.
- Users can update quantities and remove items.
- Cart totals update correctly when items change.
- The cart page is clear and accessible on mobile and desktop devices.

12. Checkout:
Implement a checkout flow for one-off shop purchases using Stripe PaymentIntents.

### Features

The checkout page must:

- Resolve the current cart for either:
  - An anonymous session.
  - A logged-in user.
- Calculate the order total, including any applicable member discounts.
- Create a Stripe PaymentIntent.
- Integrate with Stripe.js to collect and submit payment details.

After successful payment:

- Create an `Order` record.
- Create the associated `OrderItem` records.
- Mark the order status as `paid`.
- Clear the user's cart.

After failed payment:

- Display a clear error message.
- Do not create an order.
- Leave the cart intact.

### Acceptance Criteria

- Users, including logged-in users and guests, can complete checkout for the contents of their cart.
- A successful payment creates a paid `Order` with the correct items and totals.
- The cart is cleared after successful checkout.
- Failed payments do not create orders and leave the cart unchanged.

13. Website Admin:
Configure Django admin so that administrators can manage all key entities, including users, memberships, products, orders, and community content.

### Features

Register the following models in Django admin:

- `User` and `UserProfile`.
- `MembershipPlan` and `Membership`.
- `Product`, `Order`, and `OrderItem`.
- `Category`, `Thread`, and `Post`.
- `ProgressUpdate`, if implemented as a separate model.

Configure list views with useful filters and search options, such as:

- Active memberships.
- Order status.
- User accounts.
- Product status.
- Forum categories and moderation status.

Provide basic moderation capabilities, including:

- Removing or hiding inappropriate threads and posts.
- Deactivating users when necessary.

### Acceptance Criteria

- Administrators can create, view, update, and delete users, profiles, memberships, products, orders, and forum content.
- Administrators can filter and search key models.
- Administrators can moderate forum content by editing or deleting threads and posts.
- The admin interface is usable and does not display irrelevant fields.

14. Miscellaneous:
- Admin dashboard to provide overview of members, shop transactions, monthly revenue and status of each member.(Could Have).
- Search App for members, shop and community message board. (should have)
- Contact Us Page with form. (should have)

## Design Choices
### Color Scheme
### Typography
### Layout & Navigation
### Component Selection
### Responsive Design
### Wireframes

## Database Model 
### Entity Relationship Diagram

# Features

# Future Features

# Testing
## Website Navigation and Responsive Testing
## JavaScript Manual Testing
## Automated Python Testing
## Validation && Accessibility Testing
### HMTL Validation
### CSS Validation
### JavaScript Validation
### Python Validation
### Lighthouse Testing

# Code

## Code Sources and Credits

The following resources were used for guidance, implementation support, and debugging during development. Implementation
was guided by course material, official documentation, and selected tutorials, with additional adaptation and 
problem-solving carried out during development.

### BEM Methodology for css  - sources: https://getbem.com/ and https://bem.info/en/methodology/naming-convention/

## Bugs and Fixes
### AllAuth
- I encountered several deprecation errors using settings from the 0.50 version of allauth. I resolved by replacing deprecated settings with the new ones.
### Stripe 
### Stripe
### Django

# Tools and Resources
**Development Environment:**
- PyCharm for code editing and debugging
- GitHub for version control
- Heroku for deployment

**Languages & Frameworks:**
- HTML5, CSS, JavaScript ES8 for frontend development
- Bootstrap 5.3 for responsive design and components
- Python 3.12 for backend development
- Django 5.2. framework for web application architecture

**Libraries & UI Components:**
- Font Awesome for icons

**Validation & Testing Tools:**
- W3C Markup Validation Service and djlint Python package for HTML validation
- W3C CSS Validation Service for CSS validation
- JSHint for JavaScript linting and error checking
- Lighthouse for performance and accessibility testing

**Content & Design Tools:**
- Perplexity for discovery, text content generation, and drafting documentation. 
- Canva for wireframing and image editing
- Artlist.io for generative image creation
- Draw.io for entity relationship model

# Deployment

## Heroku

### Deployment Steps

### Required Configuration Variables

### Local Deployment