# ECS Fargate service notes

- `presentation-service`: internet-facing service behind an Application Load Balancer.
- `workflow-service`: internal ECS service reachable only within the VPC.
- `data-service`: internal ECS service reachable only within the VPC.
- Place all 3 services in the same VPC and private subnets, except the ALB which spans public subnets.
- Register `workflow-service` and `data-service` in Cloud Map or expose them through internal target groups so service-to-service HTTP calls stay private.
- Give `workflow-service` an IAM task role with `sqs:SendMessage` on the submission queue.
- Give `result-update-fn` network access to the internal `data-service` endpoint.
