# `erob_moveit_runtime`

Shared ROS 2/MoveIt runtime used by ZeroErr and Fairino configuration packages.
It contains the Python controller, backend facade, motion planning/execution,
state publication, API adapters and C++ planning/trajectory helpers. Robot models,
launch composition and profile values belong to the robot configuration package.

## Entry points and responsibilities

- `scripts/main.py`: starts HTTP with asynchronous runtime initialization;
  `EROB_RUNTIME_HEADLESS` selects operation without the Qt event loop.
- `scripts/runtime_initializer.py`: initializes ROS, `RobotController` and the
  backend selected by the active package/profile.
- `scripts/robot_controller.py`: owns ROS clients, motion coordination, state,
  workspace safety and the motion interlock.
- `scripts/rest/main.py`: standalone REST entry point.
- `scripts/rest/server.py`: HTTP startup, readiness gate and API composition.
- `scripts/rest/routes/`: thin routes for Configuration, Motion, State and Control.
- `scripts/runtime_api/`: typed requests/responses, validation and error mapping.
- `scripts/runtime_gateway/`: transport-independent contract, local implementation
  and ROS/diagnostic adapters.
- `scripts/configuration/`: profile validation, revisions, atomic YAML storage and
  runtime application; saving and applying are separate outcomes.
- `scripts/backend/`: robot-style backend facade used behind the gateway.
- `scripts/motion/`: planning, execution, Servo and stop strategies.
- `scripts/runtime_websockets/`: state, execution and sensor streams.

```text
HTTP client -> rest/routes -> ConfigurationApi / MotionApi / StateApi / ControlApi
                          -> RuntimeGateway -> LocalRuntimeGateway
                          -> configuration services / backend / RobotController
                          -> ROS services, actions and controllers
```

All four API groups follow this boundary. The legacy `RuntimeApi` facade delegates
to them. WebSocket servers retain their own stream implementations in the same
process; a remote ROS gateway and API process separation are future work.

Configuration persists per robot profile. The backend can start and load those
files without the platform. A UI save uses the backend configuration API and must
check `pending_application`; it does not automatically restart or recalibrate.

Motion acceptance does not prove completion. Nonblocking/queued requests return
202; blocking completions return 200. Inspect typed `error_info` and execution
state when commands fail or have an unknown outcome. Collision reset keeps motion
interlocked until fresh matching observer readiness is confirmed.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API/gateway contracts and extension rules](docs/runtime_api_architecture.md)
- [REST routes](docs/REST_API.md) and [request flows](docs/API_ENDPOINT_FLOWS.md)
- [Profile configuration API](docs/backend_configuration.md)
- [Motion and safety](docs/MOTION_AND_SAFETY.md)
- [Build and launch](../../../../BUILD_SCRIPTS_README.md)
- [Backend documentation index](../../../../../docs/README.md)

The running backend serves `/docs`, `/api/docs` and `/openapi.json`.
