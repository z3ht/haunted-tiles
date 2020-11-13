def mock_obs(rl_agents, game_state):
    agents_obs = {}
    for name, agent in rl_agents.items():
        agents_obs[name] = agent.interpret_game_state(game_state)
    return agents_obs


def mock_format_actions(rl_agents, raw_actions_dict):
    formatted_actions = {}
    for agent_name, agent in rl_agents.items():
        formatted_actions[agent_name] = agent.format_action(raw_actions_dict[agent_name])
    return formatted_actions
