ETHIO TELECOM PACKAGES STORE — UPDATED BOT FILES

Included:
- main.py
- server.py

Prepared changes:
1. Customer home menu: Browse Packages, My Orders, language, and support.
2. /start returns to the home menu and clears unfinished conversation steps.
3. Active packages appear together in one catalogue screen, with one button per package.
4. Selecting a package opens its detail screen with Buy Now and Back.
5. Payment method selection and payment instructions reuse the same editable screen.
6. Customers can view their latest 15 orders and statuses.
7. Admin orders are separated into queues: awaiting verification, awaiting delivery,
   completed, rejected, and cancelled.
8. /cancel is registered as a command.
9. Existing Supabase tables and manual payment verification/delivery workflow are retained.

IMPORTANT:
- These files are based on the main.py and server.py uploaded in this conversation.
- No Supabase schema change or Render environment-variable change is required.
- Back up the current GitHub files before replacing them.
- This prepared update does NOT yet include owner promotional broadcasts or the final
  consolidation of all admin package/payment management lists into one screen. Those
  should be added in a separate update after this version is tested.

Deployment:
1. Download and extract the ZIP.
2. Replace main.py and server.py in the existing GitHub repository.
3. Commit the changes; Render should redeploy automatically.
4. Test /start, package catalogue, package details, payment method selection,
   receipt upload, phone number submission, My Orders, and /admin order queues.
