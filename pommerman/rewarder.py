import numpy as np

# TODO add bomb place offset (how many time steps back was bomb placed that caused reward)


class Rewarder():

    def __init__(self,
                 collect_bomb=True,
                 collect_kick=True,
                 collect_range=True,
                 enemy_dead=True,
                 explode_crate=True,
                 teammate_dead=True,
                 bomb_offset=True):

        self.collect_bomb = collect_bomb
        self.collect_kick = collect_kick
        self.collect_range = collect_range
        self.enemy_dead = enemy_dead
        self.explode_crate = explode_crate
        self.teammate_dead = teammate_dead
        self.bomb_offset = bomb_offset

    def __call__(self, rewards, board, prev_board, agents, prev_kick, bombs, flames):
        for idx, agent in enumerate(agents):
            if self.bomb_offset:
                reward = [[-1, rewards[idx]]]
            else:
                reward = rewards[idx]
            if not agent.is_alive:
                if self.bomb_offset:
                    reward = [[-1, -1]]
                else:
                    reward = -1
                    continue

            if self.collect_bomb:
                reward += self.calc_collect_bomb(
                    agent.position,
                    prev_board)
            if self.collect_kick:
                reward += self.calc_collect_kick(
                    agent.position,
                    prev_board, prev_kick[idx])
            if self.collect_range:
                reward += self.calc_collect_range(
                    agent.position,
                    prev_board)
            if self.enemy_dead:
                reward += self.calc_enemy_dead(
                    agent,
                    [enemy.value for enemy in agent.enemies],
                    board, prev_board, flames)
            if self.explode_crate:
                reward += self.calc_explode_crate(
                    agent, prev_board, flames)
            if self.teammate_dead:
                reward += self.calc_teammate_dead(
                    agent,
                    agent.teammate.value,
                    board, prev_board, flames)
            reward = np.array(reward)
            reward = [[idx, reward[:, 1][reward[:, 0] == idx].sum()]
                      for idx in np.unique(reward[:, 0])]
            reward = np.array(reward)
            reward = reward[np.argsort(reward[:, 0])][::-1]
            rewards[idx] = reward

        return rewards

    def calc_collect_bomb(self, pos, prev_board):
        if prev_board[pos] == 6:
            if self.bomb_offset:
                return [[-1, 0.1]]
            return 0.1
        if self.bomb_offset:
            return []
        return 0

    def calc_collect_kick(self, pos, prev_board, kick):
        if (prev_board[pos] == 8) and not kick:
            if self.bomb_offset:
                return [[-1, 0.1]]
            return 0.1
        if self.bomb_offset:
            return []
        return 0.1

    def calc_collect_range(self, pos, prev_board):
        if prev_board[pos] == 7:
            if self.bomb_offset:
                return [[-1, 0.1]]
            return 0.1
        if self.bomb_offset:
            return []
        return 0

    def calc_enemy_dead(self, agent, enemies, board, prev_board, flames):
        enemy_dead = sum(
            [(prev_board == enemy) * int(enemy not in board) for enemy in enemies])
        if self.bomb_offset:
            reward = []
        else:
            reward = 0
        if not enemy_dead.any():
            return reward
        enemy_pos = np.where(enemy_dead.astype(bool))
        for x, y in zip(*enemy_pos):
            for flame in flames:
                if agent.agent_id != flame.bomber.agent_id:
                    continue
                if flame.position[0] == x and flame.position[1] == y:
                    if self.bomb_offset:
                        reward += [[-(12 - flame.life), 0.25]]
                    else:
                        reward += 0.25
                    break
        return reward

    def calc_explode_crate(self, agent, prev_board, flames):
        if self.bomb_offset:
            reward = []
        else:
            reward = 0
        prev_board = prev_board.copy()
        for flame in flames:
            if flame.life < 2 or agent.agent_id != flame.bomber.agent_id:
                continue
            if prev_board[flame.position] == 2:
                if self.bomb_offset:
                    reward += [[-10, 0.02]]
                else:
                    reward += 0.02
                prev_board[flame.position] = 0
        return reward

    def calc_teammate_dead(self, agent, teammate, board, prev_board, flames):
        teammate_dead = (prev_board == teammate) * int(teammate not in board)
        if self.bomb_offset:
            reward = []
        else:
            reward = 0
        if not teammate_dead.any():
            return reward
        teammate_pos = np.where(teammate_dead.astype(bool))
        for x, y in zip(*teammate_pos):
            for flame in flames:
                if agent.agent_id != flame.bomber.agent_id:
                    continue
                if flame.position[0] == x and flame.position[1] == y:
                    if self.bomb_offset:
                        reward += [[-(13 - flame.life), -0.25]]
                    else:
                        reward += -0.25
                    break
        return reward
