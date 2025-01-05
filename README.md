# SwitchVibes

This is the back-end API service for SwitchVibes, a platform that enables seamless music playlist migration between different music streaming services. Simply provide the link to a playlist from your favorite source platform (e.g., Spotify), and SwitchVibes will automatically transfer all the songs to a new playlist in your specified destination platform. Eliminate manual playlist recreation and let SwitchVibes do the heavy lifting for you.

## New Features

- **WebSockets for Real-Time Feedback**: The platform now supports WebSocket connections, allowing real-time feedback on playlist migration. Users receive immediate updates on tracks that are found or not found during the migration process, rather than waiting for the entire playlist migration to complete.
- **HTTP Request Limitations**: HTTP-based playlist migration may timeout if the playlist contains a large number of tracks. In the future, a limit will be introduced to restrict HTTP migrations to playlists with a maximum number of tracks.

## API Documentation

You can explore the endpoints and their functionalities using ReDoc and Swagger documentation:

- [ReDoc Documentation](https://switch-vibes-production.up.railway.app/docs/)
- [Swagger Documentation](https://switch-vibes-production.up.railway.app/swagger/)

## Front-end

You can interact with the API through the frontend [here](https://switch-vibes.vercel.app/). View the source code [here](https://github.com/Sucodes/switch-vibes).

Credit: [Suvwe](https://github.com/Sucodes).

## How to Use

To use SwitchVibes, you can:

- **Make HTTP Requests**: Directly interact with our API using HTTP endpoints.
- **Use WebSockets**: For a better experience with real-time feedback during playlist migration.
- **Try the Front-End**: Use our user-friendly interface to migrate your playlists effortlessly.

## Contributing

If you find any issues or have ideas to improve the project, feel free to open an issue or submit a pull request.

## Contact

Say hello to me on:

- [Twitter](https://twitter.com/yensouchenna)
- [LinkedIn](https://linkedin.com/in/onyenso)

Happy playlist migration with SwitchVibes!
